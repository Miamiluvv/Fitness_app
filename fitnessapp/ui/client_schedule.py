from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ClientScheduleWidget(QWidget):
    def __init__(self, db, client_id):
        super().__init__()
        self.db = db
        self.client_id = client_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Мое расписание и запись")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Group Classes
        layout.addWidget(QLabel("Мои записи на групповые занятия:"))
        self.group_classes_table = QTableWidget()
        self.group_classes_table.setColumnCount(5)
        self.group_classes_table.setHorizontalHeaderLabels(['ID Записи', 'Занятие', 'Дата', 'Время', 'Статус'])
        self.group_classes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.group_classes_table)

        cancel_class_btn = QPushButton("Отменить запись на групповое занятие")
        cancel_class_btn.clicked.connect(self.cancel_class_enrollment)
        layout.addWidget(cancel_class_btn)

        # Personal Training
        layout.addWidget(QLabel("Мои персональные тренировки:"))
        self.personal_training_table = QTableWidget()
        self.personal_training_table.setColumnCount(5)
        self.personal_training_table.setHorizontalHeaderLabels(['ID Сессии', 'Тренер', 'Дата и время', 'Длительность', 'Статус'])
        self.personal_training_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.personal_training_table)

        cancel_training_btn = QPushButton("Отменить запись на персональную тренировку")
        cancel_training_btn.clicked.connect(self.cancel_personal_training)
        layout.addWidget(cancel_training_btn)

        self.setLayout(layout)
        self.load_enrollments()

    def cancel_class_enrollment(self):
        selected_items = self.group_classes_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите занятие для отмены.")
            return

        enrollment_id = self.group_classes_table.item(selected_items[0].row(), 0).text()
        reply = QMessageBox.question(self, 'Подтверждение', 'Вы уверены, что хотите отменить запись?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM class_enrollments WHERE enrollment_id = %s"
            rows_affected = self.db.execute_update(query, (enrollment_id,))
            if rows_affected > 0:
                QMessageBox.information(self, "Успех", "Запись успешно отменена.")
                self.load_enrollments()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось отменить запись.")

    def cancel_personal_training(self):
        selected_items = self.personal_training_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для отмены.")
            return

        session_id = self.personal_training_table.item(selected_items[0].row(), 0).text()
        reply = QMessageBox.question(self, 'Подтверждение', 'Вы уверены, что хотите отменить запись?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM personal_training_sessions WHERE session_id = %s"
            rows_affected = self.db.execute_update(query, (session_id,))
            if rows_affected > 0:
                QMessageBox.information(self, "Успех", "Запись успешно отменена.")
                self.load_enrollments()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось отменить запись.")

    def load_enrollments(self):
        # Group classes
        query_group = """SELECT ce.enrollment_id, gc.name, ce.class_date, cs.start_time, ce.attendance_status
                       FROM class_enrollments ce
                       JOIN class_schedule cs ON ce.schedule_id = cs.schedule_id
                       JOIN group_classes gc ON cs.class_id = gc.class_id
                       WHERE ce.client_id = %s ORDER BY ce.class_date DESC"""
        results_group = self.db.execute_query(query_group, (self.client_id,))
        self.group_classes_table.setRowCount(0)
        if results_group:
            for row_idx, row_data in enumerate(results_group):
                self.group_classes_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    self.group_classes_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        # Personal training
        query_personal = """SELECT pts.session_id, CONCAT(t.first_name, ' ', t.last_name), pts.session_date, pts.duration_minutes, pts.status
                          FROM personal_training_sessions pts
                          JOIN trainers t ON pts.trainer_id = t.trainer_id
                          WHERE pts.client_id = %s ORDER BY pts.session_date DESC"""
        results_personal = self.db.execute_query(query_personal, (self.client_id,))
        self.personal_training_table.setRowCount(0)
        if results_personal:
            for row_idx, row_data in enumerate(results_personal):
                self.personal_training_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    self.personal_training_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
