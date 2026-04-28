from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class FeedbackManagementWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Управление обратной связью")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.feedback_table = QTableWidget()
        self.feedback_table.setColumnCount(6)
        self.feedback_table.setHorizontalHeaderLabels(['ID', 'Клиент', 'Тип', 'Содержание', 'Дата', 'Статус'])
        self.feedback_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.feedback_table)

        # Controls for updating status
        control_layout = QHBoxLayout()
        self.feedback_id_combo = QComboBox()
        control_layout.addWidget(QLabel("ID Обращения:"))
        control_layout.addWidget(self.feedback_id_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(['new', 'in_progress', 'resolved'])
        control_layout.addWidget(QLabel("Новый статус:"))
        control_layout.addWidget(self.status_combo)

        update_btn = QPushButton("Обновить статус")
        update_btn.clicked.connect(self.update_status)
        control_layout.addWidget(update_btn)
        layout.addLayout(control_layout)

        self.setLayout(layout)
        self.load_feedback()

    def load_feedback(self):
        query = """SELECT f.feedback_id, CONCAT(c.first_name, ' ', c.last_name), f.feedback_type, f.content, f.created_at, f.status 
                   FROM feedback f JOIN clients c ON f.client_id = c.client_id ORDER BY f.created_at DESC"""
        results = self.db.execute_query(query)
        self.feedback_table.setRowCount(0)
        self.feedback_id_combo.clear()
        if results:
            for row_idx, row_data in enumerate(results):
                self.feedback_table.insertRow(row_idx)
                self.feedback_id_combo.addItem(str(row_data[0]), row_data[0])
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.feedback_table.setItem(row_idx, col_idx, item)

    def update_status(self):
        feedback_id = self.feedback_id_combo.currentData()
        new_status = self.status_combo.currentText()
        if not feedback_id:
            QMessageBox.warning(self, "Ошибка", "Выберите обращение для обновления.")
            return

        query = "UPDATE feedback SET status = %s WHERE feedback_id = %s"
        rows_affected = self.db.execute_update(query, (new_status, feedback_id))
        if rows_affected > 0:
            QMessageBox.information(self, "Успех", "Статус обращения обновлен.")
            self.load_feedback()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось обновить статус.")
