from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDoubleSpinBox, QTextEdit, QMessageBox, QComboBox
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont

class RecordProgressDialog(QDialog):
    def __init__(self, db, trainer_id, on_success):
        super().__init__()
        self.db = db
        self.trainer_id = trainer_id
        self.on_success = on_success
        self.setWindowTitle("Зафиксировать Прогресс Клиента")
        self.init_ui()
        self.load_clients()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите клиента:"))
        self.client_combo = QComboBox()
        layout.addWidget(self.client_combo)

        layout.addWidget(QLabel("Вес (кг):"))
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 300)
        layout.addWidget(self.weight_input)

        layout.addWidget(QLabel("Рост (см):"))
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(0, 300)
        layout.addWidget(self.height_input)

        layout.addWidget(QLabel("Процент жира (%):"))
        self.body_fat_input = QDoubleSpinBox()
        self.body_fat_input.setRange(0, 100)
        layout.addWidget(self.body_fat_input)

        layout.addWidget(QLabel("Заметки:"))
        self.notes_input = QTextEdit()
        layout.addWidget(self.notes_input)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_progress)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def load_clients(self):
        # Load clients assigned to this trainer for personal sessions or group classes
        query = """SELECT DISTINCT c.client_id, CONCAT(c.first_name, ' ', c.last_name)
                   FROM clients c
                   WHERE c.client_id IN (SELECT client_id FROM personal_training_sessions WHERE trainer_id = %s)
                   OR c.client_id IN (SELECT ce.client_id FROM class_enrollments ce JOIN class_schedule cs ON ce.schedule_id = cs.schedule_id JOIN group_classes gc ON cs.class_id = gc.class_id WHERE gc.trainer_id = %s)
                """
        results = self.db.execute_query(query, (self.trainer_id, self.trainer_id))
        if results:
            for client_id, name in results:
                self.client_combo.addItem(name, client_id)

    def save_progress(self):
        client_id = self.client_combo.currentData()
        weight = self.weight_input.value()
        height = self.height_input.value()
        body_fat = self.body_fat_input.value()
        notes = self.notes_input.toPlainText()

        if not client_id:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента.")
            return

        query = "INSERT INTO client_progress (client_id, measurement_date, weight, height, body_fat_percentage, notes) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (client_id, QDate.currentDate().toString('yyyy-MM-dd'), weight, height, body_fat, notes)
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", "Прогресс клиента сохранен.")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить прогресс.")
