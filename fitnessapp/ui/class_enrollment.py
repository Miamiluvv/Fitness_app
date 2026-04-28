from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QMessageBox, QHeaderView, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class ClassEnrollmentWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Запись на занятия")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Enrollment section
        enroll_layout = QHBoxLayout()
        
        enroll_layout.addWidget(QLabel("ID клиента:"))
        self.client_id_input = QLineEdit()
        enroll_layout.addWidget(self.client_id_input)
        
        enroll_layout.addWidget(QLabel("Расписание:"))
        self.schedule_combo = QComboBox()
        enroll_layout.addWidget(self.schedule_combo)
        
        enroll_layout.addWidget(QLabel("Дата занятия:"))
        self.class_date_input = QDateEdit()
        self.class_date_input.setDate(QDate.currentDate())
        enroll_layout.addWidget(self.class_date_input)
        
        enroll_btn = QPushButton("Записать")
        enroll_btn.clicked.connect(self.enroll_client)
        enroll_layout.addWidget(enroll_btn)
        
        layout.addLayout(enroll_layout)
        
        # Enrollments list
        layout.addWidget(QLabel("Записи на занятия:"))
        self.enrollments_table = QTableWidget()
        self.enrollments_table.setColumnCount(8)
        self.enrollments_table.setHorizontalHeaderLabels(['ID записи', 'ID клиента', 'Занятие', 'День', 'Время', 'Дата', 'Статус', 'Дата записи'])
        self.enrollments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.enrollments_table)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Фильтр по дате:"))
        self.filter_date = QDateEdit()
        self.filter_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.filter_date)
        
        filter_btn = QPushButton("Применить фильтр")
        filter_btn.clicked.connect(self.load_enrollments)
        filter_layout.addWidget(filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Refresh button
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_data()

    def enroll_client(self):
        client_id = self.client_id_input.text()
        schedule_id = self.schedule_combo.currentData()
        class_date = self.class_date_input.date().toString('yyyy-MM-dd')
        
        if not client_id or not schedule_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, заполните все поля")
            return
        
        # Check if client has group classes access
        query = """
        SELECT m.membership_id FROM memberships m
        JOIN membership_types mt ON m.membership_type_id = mt.membership_type_id
        WHERE m.client_id = %s AND m.status = 'active' AND m.end_date >= CURDATE()
        AND mt.group_classes_access = TRUE
        LIMIT 1
        """
        result = self.db.execute_query(query, (client_id,))
        
        if not result:
            QMessageBox.critical(self, "Ошибка", "У клиента нет активного абонемента с доступом к групповым занятиям")
            return
        
        # Check if class is not full
        query = """
        SELECT gc.max_participants, COUNT(ce.enrollment_id) as enrolled
        FROM class_schedule cs
        JOIN group_classes gc ON cs.class_id = gc.class_id
        LEFT JOIN class_enrollments ce ON cs.schedule_id = ce.schedule_id AND ce.class_date = %s
        WHERE cs.schedule_id = %s
        GROUP BY gc.class_id
        """
        result = self.db.execute_query(query, (class_date, schedule_id))
        
        if result:
            max_participants, enrolled = result[0]
            if enrolled >= max_participants:
                QMessageBox.critical(self, "Ошибка", "Занятие полностью заполнено")
                return
        
        # Enroll client
        insert_query = """
        INSERT INTO class_enrollments (client_id, schedule_id, class_date)
        VALUES (%s, %s, %s)
        """
        result = self.db.execute_insert(insert_query, (client_id, schedule_id, class_date))
        
        if result:
            QMessageBox.information(self, "Успех", f"Клиент записан с ID: {result}")
            self.client_id_input.clear()
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось записать клиента")

    def load_data(self):
        # Load schedules
        query = """
        SELECT cs.schedule_id, CONCAT(gc.name, ' - ', cs.day_of_week, ' ', cs.start_time)
        FROM class_schedule cs
        JOIN group_classes gc ON cs.class_id = gc.class_id
        ORDER BY cs.day_of_week, cs.start_time
        """
        results = self.db.execute_query(query)
        
        self.schedule_combo.clear()
        if results:
            for schedule_id, schedule_info in results:
                self.schedule_combo.addItem(schedule_info, schedule_id)
        
        self.load_enrollments()

    def load_enrollments(self):
        filter_date = self.filter_date.date().toString('yyyy-MM-dd')
        
        query = """
        SELECT ce.enrollment_id, ce.client_id, gc.name, cs.day_of_week, cs.start_time,
               ce.class_date, ce.attendance_status, ce.enrollment_date
        FROM class_enrollments ce
        JOIN class_schedule cs ON ce.schedule_id = cs.schedule_id
        JOIN group_classes gc ON cs.class_id = gc.class_id
        WHERE ce.class_date = %s
        ORDER BY cs.day_of_week, cs.start_time
        """
        results = self.db.execute_query(query, (filter_date,))
        
        self.enrollments_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.enrollments_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.enrollments_table.setItem(row_idx, col_idx, item)
