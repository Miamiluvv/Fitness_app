from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QDate

class EnrollClassDialog(QDialog):
    def __init__(self, db, client_id, on_success):
        super().__init__()
        self.db = db
        self.client_id = client_id
        self.on_success = on_success
        self.setWindowTitle("Запись на групповое занятие")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите занятие:"))
        self.schedule_combo = QComboBox()
        query = '''SELECT cs.schedule_id, CONCAT(gc.name, ' - ', cs.day_of_week, ' ', cs.start_time) FROM class_schedule cs JOIN group_classes gc ON cs.class_id = gc.class_id'''
        results = self.db.execute_query(query)
        if results:
            for schedule_id, info in results:
                self.schedule_combo.addItem(info, schedule_id)
        self.schedule_combo.currentIndexChanged.connect(self.update_available_dates)
        layout.addWidget(self.schedule_combo)

        layout.addWidget(QLabel("Дата занятия:"))
        self.class_date_combo = QComboBox()
        layout.addWidget(self.class_date_combo)

        enroll_btn = QPushButton("Записаться")
        enroll_btn.clicked.connect(self.enroll)
        layout.addWidget(enroll_btn)
        self.setLayout(layout)
        self.update_available_dates()

    def update_available_dates(self):
        self.class_date_combo.clear()
        schedule_id = self.schedule_combo.currentData()
        if not schedule_id:
            return

        query = "SELECT day_of_week FROM class_schedule WHERE schedule_id = %s"
        result = self.db.execute_query(query, (schedule_id,))
        if not result:
            return

        day_of_week_str = result[0][0]
        day_map = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        target_day = day_map.get(day_of_week_str)

        if not target_day:
            return

        today = QDate.currentDate()
        days_ahead = target_day - today.dayOfWeek()
        if days_ahead < 0:
            days_ahead += 7
        
        next_date = today.addDays(days_ahead)
        for i in range(4): # Generate dates for the next 4 weeks
            date_to_add = next_date.addDays(i * 7)
            self.class_date_combo.addItem(date_to_add.toString('yyyy-MM-dd'), date_to_add)

    def enroll(self):
        schedule_id = self.schedule_combo.currentData()
        class_date_str = self.class_date_combo.currentText()
        # Проверка доступа к групповым занятиям
        query = '''SELECT m.membership_id FROM memberships m JOIN membership_types mt ON m.membership_type_id = mt.membership_type_id WHERE m.client_id = %s AND m.status = 'active' AND m.end_date >= CURDATE() AND mt.group_classes_access = TRUE LIMIT 1'''
        result = self.db.execute_query(query, (self.client_id,))
        if not result:
            QMessageBox.critical(self, "Ошибка", "Нет активного абонемента с доступом к групповым занятиям")
            return
        # Проверка лимита
        query = '''SELECT gc.max_participants, COUNT(ce.enrollment_id) FROM class_schedule cs JOIN group_classes gc ON cs.class_id = gc.class_id LEFT JOIN class_enrollments ce ON cs.schedule_id = ce.schedule_id AND ce.class_date = %s WHERE cs.schedule_id = %s GROUP BY gc.class_id'''
        result = self.db.execute_query(query, (class_date_str, schedule_id))
        if result:
            max_participants, enrolled = result[0]
            if enrolled >= max_participants:
                QMessageBox.critical(self, "Ошибка", "Занятие заполнено")
                return
        # Записать клиента
        insert_query = '''INSERT INTO class_enrollments (client_id, schedule_id, class_date) VALUES (%s, %s, %s)'''
        result = self.db.execute_insert(insert_query, (self.client_id, schedule_id, class_date_str))
        if result:
            QMessageBox.information(self, "Успех", "Вы успешно записаны!")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось записать на занятие")
