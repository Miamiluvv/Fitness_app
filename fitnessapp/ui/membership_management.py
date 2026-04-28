from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDateEdit,
                             QComboBox, QMessageBox, QHeaderView, QSpinBox, QDoubleSpinBox,
                             QCheckBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

class MembershipManagementWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Управление абонементами")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabs for membership types and memberships
        tab_layout = QHBoxLayout()
        
        # Left side - Membership Types
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Типы абонементов:"))
        
        form_layout = QVBoxLayout()
        
        form_layout.addWidget(QLabel("Название типа:"))
        self.type_name_input = QLineEdit()
        form_layout.addWidget(self.type_name_input)
        
        form_layout.addWidget(QLabel("Длительность (дни):"))
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(1)
        self.duration_input.setMaximum(365)
        form_layout.addWidget(self.duration_input)
        
        form_layout.addWidget(QLabel("Цена:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(10000)
        form_layout.addWidget(self.price_input)
        
        form_layout.addWidget(QLabel("Лимит посещений (0 = неограниченно):"))
        self.visits_limit_input = QSpinBox()
        self.visits_limit_input.setMinimum(0)
        self.visits_limit_input.setMaximum(1000)
        form_layout.addWidget(self.visits_limit_input)
        
        # Checkboxes for access
        self.gym_access_check = QCheckBox("Доступ в тренажерный зал")
        self.gym_access_check.setChecked(True)
        form_layout.addWidget(self.gym_access_check)
        
        self.pool_access_check = QCheckBox("Доступ в бассейн")
        form_layout.addWidget(self.pool_access_check)
        
        self.classes_access_check = QCheckBox("Доступ к групповым занятиям")
        form_layout.addWidget(self.classes_access_check)
        
        left_layout.addLayout(form_layout)
        
        add_type_btn = QPushButton("Добавить тип абонемента")
        add_type_btn.clicked.connect(self.add_membership_type)
        left_layout.addWidget(add_type_btn)
        
        left_layout.addWidget(QLabel("Доступные типы:"))
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(7)
        self.types_table.setHorizontalHeaderLabels(['ID', 'Название', 'Дни', 'Цена', 'Зал', 'Бассейн', 'Занятия'])
        self.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.types_table)
        
        # Right side - Sell Membership
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Продажа абонемента:"))
        
        sell_form = QVBoxLayout()
        
        sell_form.addWidget(QLabel("ID клиента:"))
        self.client_id_input = QLineEdit()
        sell_form.addWidget(self.client_id_input)
        
        sell_form.addWidget(QLabel("Тип абонемента:"))
        self.membership_type_combo = QComboBox()
        sell_form.addWidget(self.membership_type_combo)
        
        sell_form.addWidget(QLabel("Дата начала:"))
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        sell_form.addWidget(self.start_date_input)
        
        sell_form.addWidget(QLabel("Размер скидки:"))
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMinimum(0)
        self.discount_input.setMaximum(10000)
        sell_form.addWidget(self.discount_input)
        
        right_layout.addLayout(sell_form)
        
        sell_btn = QPushButton("Продать абонемент")
        sell_btn.clicked.connect(self.sell_membership)
        right_layout.addWidget(sell_btn)
        
        right_layout.addWidget(QLabel("Активные абонементы:"))
        self.memberships_table = QTableWidget()
        self.memberships_table.setColumnCount(8)
        self.memberships_table.setHorizontalHeaderLabels(['ID', 'ID клиента', 'Тип', 'Дата начала', 'Дата окончания', 'Цена', 'Осталось', 'Статус'])
        self.memberships_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.memberships_table)

        # Membership status management
        status_layout = QHBoxLayout()
        freeze_btn = QPushButton("Заморозить")
        freeze_btn.clicked.connect(lambda: self.update_membership_status('frozen'))
        status_layout.addWidget(freeze_btn)

        activate_btn = QPushButton("Активировать")
        activate_btn.clicked.connect(lambda: self.update_membership_status('active'))
        status_layout.addWidget(activate_btn)

        right_layout.addLayout(status_layout)
        
        tab_layout.addLayout(left_layout)
        tab_layout.addLayout(right_layout)
        layout.addLayout(tab_layout)
        
        # Refresh button
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_data()

    def add_membership_type(self):
        name = self.type_name_input.text()
        duration = self.duration_input.value()
        price = self.price_input.value()
        visits_limit = self.visits_limit_input.value()
        gym = self.gym_access_check.isChecked()
        pool = self.pool_access_check.isChecked()
        classes = self.classes_access_check.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, введите название типа абонемента")
            return
        
        query = """
        INSERT INTO membership_types (name, duration_days, price, gym_access, pool_access, group_classes_access, visits_limit)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (name, duration, price, gym, pool, classes, visits_limit if visits_limit > 0 else None)
        
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", "Тип абонемента добавлен")
            self.type_name_input.clear()
            self.duration_input.setValue(30)
            self.price_input.setValue(0)
            self.visits_limit_input.setValue(0)
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить тип абонемента")


    def sell_membership(self):
        client_id = self.client_id_input.text()
        membership_type_id = self.membership_type_combo.currentData()
        start_date = self.start_date_input.date().toString('yyyy-MM-dd')
        discount = self.discount_input.value()
        if not client_id or not membership_type_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, выберите клиента и тип абонемента")
            return
        query = "SELECT duration_days, price FROM membership_types WHERE membership_type_id = %s"
        result = self.db.execute_query(query, (membership_type_id,))
        if not result:
            QMessageBox.critical(self, "Ошибка", "Тип абонемента не найден")
            return
        duration_days, price = result[0]
        insert_query = """
        INSERT INTO memberships (client_id, membership_type_id, start_date, end_date, price_paid, discount_applied, visits_remaining, purchase_date)
        VALUES (%s, %s, %s, DATE_ADD(%s, INTERVAL %s DAY), %s, %s, 
                (SELECT visits_limit FROM membership_types WHERE membership_type_id = %s), NOW())
        """
        params = (client_id, membership_type_id, start_date, start_date, duration_days, float(price) - discount, discount, membership_type_id)
        result = self.db.execute_insert(insert_query, params)
        if result:
            QMessageBox.information(self, "Успех", f"Абонемент продан с ID: {result}")
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось продать абонемент")

    def load_data(self):
        # Load membership types
        query = "SELECT membership_type_id, name, duration_days, price, gym_access, pool_access, group_classes_access FROM membership_types"
        results = self.db.execute_query(query)
        
        self.types_table.setRowCount(0)
        self.membership_type_combo.clear()
        if results:
            for row_idx, row_data in enumerate(results):
                self.types_table.insertRow(row_idx)
                self.membership_type_combo.addItem(row_data[1], row_data[0])
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.types_table.setItem(row_idx, col_idx, item)
        
    def update_membership_status(self, status):
        selected_items = self.memberships_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите абонемент для изменения статуса.")
            return

        membership_id = self.memberships_table.item(selected_items[0].row(), 0).text()
        query = "UPDATE memberships SET status = %s WHERE membership_id = %s"
        rows_affected = self.db.execute_update(query, (status, membership_id))
        if rows_affected > 0:
            QMessageBox.information(self, "Успех", f"Статус абонемента обновлен на '{status}'.")
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось обновить статус абонемента.")

    def load_data(self):
        # Load membership types
        query = "SELECT membership_type_id, name, duration_days, price, gym_access, pool_access, group_classes_access FROM membership_types"
        results = self.db.execute_query(query)
        
        self.types_table.setRowCount(0)
        self.membership_type_combo.clear()
        if results:
            for row_idx, row_data in enumerate(results):
                self.types_table.insertRow(row_idx)
                self.membership_type_combo.addItem(row_data[1], row_data[0])
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.types_table.setItem(row_idx, col_idx, item)
        
        # Load memberships (all statuses)
        query = """
        SELECT m.membership_id, m.client_id, mt.name, m.start_date, m.end_date, 
               m.price_paid, m.visits_remaining, m.status
        FROM memberships m
        JOIN membership_types mt ON m.membership_type_id = mt.membership_type_id
        ORDER BY m.start_date DESC
        """
        results = self.db.execute_query(query)
        
        self.memberships_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.memberships_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.memberships_table.setItem(row_idx, col_idx, item)
