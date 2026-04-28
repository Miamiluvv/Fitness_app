from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDateTimeEdit, QPushButton, QMessageBox, QSpinBox
from PyQt6.QtCore import QDateTime, QDate

class BookTrainingDialog(QDialog):
    def __init__(self, db, client_id, on_success):
        super().__init__()
        self.db = db
        self.client_id = client_id
        self.on_success = on_success
        self.setWindowTitle("Запись на персональную тренировку")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите тренера:"))
        self.trainer_combo = QComboBox()
        query = "SELECT trainer_id, CONCAT(first_name, ' ', last_name) FROM trainers WHERE status = 'active'"
        results = self.db.execute_query(query)
        if results:
            for trainer_id, name in results:
                self.trainer_combo.addItem(name, trainer_id)
        layout.addWidget(self.trainer_combo)

        layout.addWidget(QLabel("Дата и время:"))
        self.session_datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.session_datetime_input.setMinimumDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.session_datetime_input)

        layout.addWidget(QLabel("Длительность (мин):"))
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(15)
        self.duration_input.setMaximum(180)
        self.duration_input.setValue(60)
        layout.addWidget(self.duration_input)

        book_btn = QPushButton("Записаться")
        book_btn.clicked.connect(self.book)
        layout.addWidget(book_btn)
        self.setLayout(layout)

    def book(self):
        trainer_id = self.trainer_combo.currentData()
        session_datetime = self.session_datetime_input.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        duration = self.duration_input.value()
        # Проверить существование клиента
        query = "SELECT client_id FROM clients WHERE client_id = %s"
        result = self.db.execute_query(query, (self.client_id,))
        if not result:
            QMessageBox.critical(self, "Ошибка", "Клиент не найден")
            return
        # Записать тренировку
        insert_query = '''INSERT INTO personal_training_sessions (client_id, trainer_id, session_date, duration_minutes) VALUES (%s, %s, %s, %s)'''
        result = self.db.execute_insert(insert_query, (self.client_id, trainer_id, session_datetime, duration))
        if result:
            QMessageBox.information(self, "Успех", "Вы успешно записались на персональную тренировку!")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось записаться на тренировку")
