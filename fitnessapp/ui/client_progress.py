from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ClientProgressWidget(QWidget):
    def __init__(self, db, client_id):
        super().__init__()
        self.db = db
        self.client_id = client_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Мой прогресс")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(6)
        self.progress_table.setHorizontalHeaderLabels(['ID', 'Дата', 'Вес', 'Рост', 'Процент жира', 'Заметки'])
        self.progress_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.progress_table)

        self.setLayout(layout)
        self.load_progress()

    def load_progress(self):
        query = "SELECT progress_id, measurement_date, weight, height, body_fat_percentage, notes FROM client_progress WHERE client_id = %s ORDER BY measurement_date DESC"
        results = self.db.execute_query(query, (self.client_id,))
        self.progress_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.progress_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.progress_table.setItem(row_idx, col_idx, item)
