from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDateTimeEdit, QLineEdit, QMessageBox
from PyQt6.QtCore import QDateTime

class BlockTimeDialog(QDialog):
    def __init__(self, db, trainer_id, on_success):
        super().__init__()
        self.db = db
        self.trainer_id = trainer_id
        self.on_success = on_success
        self.setWindowTitle("Заблокировать Время")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Время начала:"))
        self.start_time_input = QDateTimeEdit(QDateTime.currentDateTime())
        layout.addWidget(self.start_time_input)

        layout.addWidget(QLabel("Время окончания:"))
        self.end_time_input = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))
        layout.addWidget(self.end_time_input)

        layout.addWidget(QLabel("Причина:"))
        self.reason_input = QLineEdit()
        layout.addWidget(self.reason_input)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_blocked_time)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_blocked_time(self):
        start_time = self.start_time_input.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        end_time = self.end_time_input.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        reason = self.reason_input.text()

        query = "INSERT INTO trainer_availability (trainer_id, start_time, end_time, reason) VALUES (%s, %s, %s, %s)"
        params = (self.trainer_id, start_time, end_time, reason)
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", "Время успешно заблокировано.")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось заблокировать время.")
