from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import csv

class FinancialReportWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Финансовый отчет")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(['Тип абонемента', 'Продано', 'Общая выручка', 'Скидки', 'Чистая выручка'])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.report_table)

        export_btn = QPushButton("Экспорт в CSV")
        export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(export_btn)

        self.setLayout(layout)
        self.load_report()

    def load_report(self):
        query = """SELECT mt.name, COUNT(m.membership_id), SUM(m.price_paid), SUM(m.discount_applied), (SUM(m.price_paid) - SUM(m.discount_applied))
                   FROM memberships m
                   JOIN membership_types mt ON m.membership_type_id = mt.membership_type_id
                   GROUP BY mt.name"""
        results = self.db.execute_query(query)
        self.report_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.report_table.setItem(row_idx, col_idx, item)

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "financial_report.csv", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = [self.report_table.horizontalHeaderItem(i).text() for i in range(self.report_table.columnCount())]
                writer.writerow(headers)
                for row in range(self.report_table.rowCount()):
                    row_data = [self.report_table.item(row, col).text() for col in range(self.report_table.columnCount())]
                    writer.writerow(row_data)
