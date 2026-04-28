from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QDateEdit,
                             QComboBox, QTextEdit, QMessageBox, QHeaderView, QDialog,
                             QSpinBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import re

class ClientRegistrationWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Регистрация клиента")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QHBoxLayout()
        
        # Left column
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Имя:"))
        self.first_name_input = QLineEdit()
        left_layout.addWidget(self.first_name_input)
        
        left_layout.addWidget(QLabel("Фамилия:"))
        self.last_name_input = QLineEdit()
        left_layout.addWidget(self.last_name_input)
        
        left_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        left_layout.addWidget(self.email_input)
        
        left_layout.addWidget(QLabel("Телефон:"))
        self.phone_input = QLineEdit()
        left_layout.addWidget(self.phone_input)
        
        left_layout.addWidget(QLabel("Дата рождения:"))
        self.dob_input = QDateEdit()
        self.dob_input.setDate(QDate.currentDate())
        left_layout.addWidget(self.dob_input)
        
        # Right column
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("Пол:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['М', 'Ж'])
        right_layout.addWidget(self.gender_combo)
        
        right_layout.addWidget(QLabel("Медицинские ограничения:"))
        self.medical_input = QTextEdit()
        self.medical_input.setMaximumHeight(100)
        right_layout.addWidget(self.medical_input)
        
        right_layout.addWidget(QLabel("Цели тренировок:"))
        self.goals_input = QTextEdit()
        self.goals_input.setMaximumHeight(100)
        right_layout.addWidget(self.goals_input)
        
        form_layout.addLayout(left_layout)
        form_layout.addLayout(right_layout)
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton("Зарегистрировать клиента")
        register_btn.clicked.connect(self.register_client)
        button_layout.addWidget(register_btn)
        
        clear_btn = QPushButton("Очистить")
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Table
        layout.addWidget(QLabel("Зарегистрированные клиенты:"))
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(8)
        self.clients_table.setHorizontalHeaderLabels(['ID', 'Имя', 'Фамилия', 'Email', 'Телефон', 'Дата рождения', 'Пол', 'Статус'])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.clients_table)
        
        # Refresh button
        refresh_btn = QPushButton("Обновить список")
        refresh_btn.clicked.connect(self.load_clients)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_clients()

    def register_client(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        dob = self.dob_input.date().toString('yyyy-MM-dd')
        gender = self.gender_combo.currentText()
        gender_map = {'М': 'M', 'Ж': 'F'}
        gender = gender_map.get(gender, 'M')
        medical = self.medical_input.toPlainText()
        goals = self.goals_input.toPlainText()
        if not all([first_name, last_name, email, phone]):
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, заполните все обязательные поля.")
            return

        errors = []
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append("Пожалуйста, введите корректный email.")
        if not re.match(r'^(\+7|8)\d{10}$', phone):
            errors.append("Пожалуйста, введите корректный номер телефона (например, +79... или 89...).")
        if errors:
            QMessageBox.warning(self, "Ошибка валидации", "\n".join(errors))
            return

        query = """
        INSERT INTO clients (first_name, last_name, email, phone, date_of_birth, gender, medical_restrictions, fitness_goals)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (first_name, last_name, email, phone, dob, gender, medical, goals)
        try:
            result = self.db.execute_insert(query, params)
            if result:
                QMessageBox.information(self, "Успех", f"Клиент зарегистрирован с ID: {result}")
                self.clear_form()
                self.load_clients()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось зарегистрировать клиента")
        except Exception as e:
            print(f"Registration error: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось зарегистрировать клиента")

    def clear_form(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.dob_input.setDate(QDate.currentDate())
        self.gender_combo.setCurrentIndex(0)
        self.medical_input.clear()
        self.goals_input.clear()

    def load_clients(self):
        query = "SELECT client_id, first_name, last_name, email, phone, date_of_birth, gender, status FROM clients"
        results = self.db.execute_query(query)
        
        self.clients_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.clients_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.clients_table.setItem(row_idx, col_idx, item)
