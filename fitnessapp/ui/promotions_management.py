from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QDateEdit, QHeaderView, QMessageBox, QDoubleSpinBox
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont

class PromotionsManagementWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Управление Акциями и Скидками")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Form for adding/editing promotions
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Название акции:"))
        self.name_input = QLineEdit()
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(QLabel("Процент скидки (%):"))
        self.percentage_input = QDoubleSpinBox()
        self.percentage_input.setRange(0, 100)
        form_layout.addWidget(self.percentage_input)

        form_layout.addWidget(QLabel("Сумма скидки (руб.):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 100000)
        form_layout.addWidget(self.amount_input)

        form_layout.addWidget(QLabel("Дата начала:"))
        self.start_date_input = QDateEdit(QDate.currentDate())
        form_layout.addWidget(self.start_date_input)

        form_layout.addWidget(QLabel("Дата окончания:"))
        self.end_date_input = QDateEdit(QDate.currentDate().addDays(30))
        form_layout.addWidget(self.end_date_input)

        add_btn = QPushButton("Добавить акцию")
        add_btn.clicked.connect(self.add_promotion)
        form_layout.addWidget(add_btn)
        layout.addLayout(form_layout)

        # Table of existing promotions
        self.promotions_table = QTableWidget()
        self.promotions_table.setColumnCount(7)
        self.promotions_table.setHorizontalHeaderLabels(['ID', 'Название', 'Скидка (%)', 'Скидка (сумма)', 'Начало', 'Окончание', 'Статус'])
        self.promotions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.promotions_table)

        self.setLayout(layout)
        self.load_promotions()

    def load_promotions(self):
        query = "SELECT promotion_id, name, discount_percentage, discount_amount, start_date, end_date, status FROM promotions"
        results = self.db.execute_query(query)
        self.promotions_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.promotions_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    self.promotions_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def add_promotion(self):
        name = self.name_input.text()
        percentage = self.percentage_input.value()
        amount = self.amount_input.value()
        start_date = self.start_date_input.date().toString('yyyy-MM-dd')
        end_date = self.end_date_input.date().toString('yyyy-MM-dd')

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название акции.")
            return

        query = "INSERT INTO promotions (name, discount_percentage, discount_amount, start_date, end_date) VALUES (%s, %s, %s, %s, %s)"
        params = (name, percentage if percentage > 0 else None, amount if amount > 0 else None, start_date, end_date)
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", "Акция добавлена.")
            self.load_promotions()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить акцию.")
