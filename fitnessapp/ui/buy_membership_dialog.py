from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QDate

class BuyMembershipDialog(QDialog):
    def __init__(self, db, client_id, on_success):
        super().__init__()
        self.db = db
        self.client_id = client_id
        self.on_success = on_success
        self.setWindowTitle("Покупка абонемента")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Выберите тип абонемента:"))
        self.type_combo = QComboBox()
        query = "SELECT membership_type_id, name FROM membership_types"
        results = self.db.execute_query(query)
        if results:
            for type_id, name in results:
                self.type_combo.addItem(name, type_id)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Дата начала:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        layout.addWidget(self.start_date)

        buy_btn = QPushButton("Купить")
        buy_btn.clicked.connect(self.buy)
        layout.addWidget(buy_btn)
        self.setLayout(layout)

    def buy(self):
        type_id = self.type_combo.currentData()
        start_date = self.start_date.date().toString('yyyy-MM-dd')
        # Получить длительность и цену
        query = "SELECT duration_days, price FROM membership_types WHERE membership_type_id = %s"
        result = self.db.execute_query(query, (type_id,))
        if not result:
            QMessageBox.critical(self, "Ошибка", "Тип абонемента не найден")
            return
        duration_days, price = result[0]
        # Добавить абонемент
        insert_query = '''INSERT INTO memberships (client_id, membership_type_id, start_date, end_date, price_paid, discount_applied, visits_remaining, status) VALUES (%s, %s, %s, DATE_ADD(%s, INTERVAL %s DAY), %s, 0, (SELECT visits_limit FROM membership_types WHERE membership_type_id = %s), 'active')'''
        params = (self.client_id, type_id, start_date, start_date, duration_days, price, type_id)
        result = self.db.execute_insert(insert_query, params)
        if result:
            QMessageBox.information(self, "Успех", "Абонемент успешно куплен!")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось купить абонемент")
