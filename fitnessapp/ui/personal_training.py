from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QMessageBox, QHeaderView, QDateTimeEdit, QSpinBox, QTextEdit, QDateEdit)
from PyQt6.QtCore import Qt, QDateTime, QDate
from PyQt6.QtGui import QFont

class PersonalTrainingWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Управление персональными тренировками")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Book session section
        book_layout = QHBoxLayout()
        
        book_layout.addWidget(QLabel("ID клиента:"))
        self.client_id_input = QLineEdit()
        book_layout.addWidget(self.client_id_input)
        
        book_layout.addWidget(QLabel("Тренер:"))
        self.trainer_combo = QComboBox()
        book_layout.addWidget(self.trainer_combo)
        
        book_layout.addWidget(QLabel("Дата и время:"))
        self.session_datetime = QDateTimeEdit()
        self.session_datetime.setDateTime(QDateTime.currentDateTime())
        book_layout.addWidget(self.session_datetime)
        
        book_layout.addWidget(QLabel("Длительность (мин):"))
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(15)
        self.duration_input.setMaximum(180)
        self.duration_input.setValue(60)
        book_layout.addWidget(self.duration_input)
        
        book_btn = QPushButton("Забронировать сеанс")
        book_btn.clicked.connect(self.book_session)
        book_layout.addWidget(book_btn)
        
        layout.addLayout(book_layout)
        
        # Sessions list
        layout.addWidget(QLabel("Запланированные сеансы:"))
        # Filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр по дате:"))
        self.date_filter_input = QDateEdit(QDate.currentDate())
        filter_layout.addWidget(self.date_filter_input)
        
        filter_btn = QPushButton("Фильтр")
        filter_btn.clicked.connect(lambda: self.load_sessions(filter_by_date=True))
        filter_layout.addWidget(filter_btn)

        reset_btn = QPushButton("Сбросить")
        reset_btn.clicked.connect(self.reset_filter)
        filter_layout.addWidget(reset_btn)
        layout.addLayout(filter_layout)

        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(7)
        self.sessions_table.setHorizontalHeaderLabels(['ID сеанса', 'Клиент', 'Тренер', 'Дата и время', 'Длительность', 'Статус', 'Дата бронирования'])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sessions_table)
        
        # Journal section
        journal_layout = QHBoxLayout()
        
        journal_layout.addWidget(QLabel("ID сеанса:"))
        self.session_id_input = QLineEdit()
        journal_layout.addWidget(self.session_id_input)
        
        journal_layout.addWidget(QLabel("Упражнение:"))
        self.exercise_input = QLineEdit()
        journal_layout.addWidget(self.exercise_input)
        
        journal_layout.addWidget(QLabel("Подходы:"))
        self.sets_input = QSpinBox()
        self.sets_input.setMinimum(1)
        self.sets_input.setMaximum(10)
        journal_layout.addWidget(self.sets_input)
        
        journal_layout.addWidget(QLabel("Повторения:"))
        self.reps_input = QSpinBox()
        self.reps_input.setMinimum(1)
        self.reps_input.setMaximum(100)
        journal_layout.addWidget(self.reps_input)
        
        journal_layout.addWidget(QLabel("Вес (кг):"))
        self.weight_input = QLineEdit()
        journal_layout.addWidget(self.weight_input)
        
        add_exercise_btn = QPushButton("Добавить упражнение")
        add_exercise_btn.clicked.connect(self.add_exercise)
        journal_layout.addWidget(add_exercise_btn)
        
        layout.addLayout(journal_layout)
        
        # Journal list
        layout.addWidget(QLabel("Журнал тренировок:"))
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(7)
        self.journal_table.setHorizontalHeaderLabels(['ID записи', 'ID сеанса', 'Упражнение', 'Подходы', 'Повторения', 'Вес (кг)', 'Дата'])
        self.journal_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.journal_table)
        
        # Refresh button
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_data()

    def book_session(self):
        client_id = self.client_id_input.text()
        trainer_id = self.trainer_combo.currentData()
        session_datetime = self.session_datetime.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        duration = self.duration_input.value()
        
        if not client_id or not trainer_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, заполните все поля")
            return
        
        # Check if client exists
        query = "SELECT client_id FROM clients WHERE client_id = %s"
        result = self.db.execute_query(query, (client_id,))
        
        if not result:
            QMessageBox.critical(self, "Ошибка", "Клиент не найден")
            return
        
        # Book session
        insert_query = """
        INSERT INTO personal_training_sessions (client_id, trainer_id, session_date, duration_minutes)
        VALUES (%s, %s, %s, %s)
        """
        result = self.db.execute_insert(insert_query, (client_id, trainer_id, session_datetime, duration))
        
        if result:
            QMessageBox.information(self, "Успех", f"Сеанс забронирован с ID: {result}")
            self.client_id_input.clear()
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось забронировать сеанс")

    def add_exercise(self):
        session_id = self.session_id_input.text()
        exercise = self.exercise_input.text()
        sets = self.sets_input.value()
        reps = self.reps_input.value()
        weight = self.weight_input.text()
        
        if not session_id or not exercise:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, заполните обязательные поля")
            return
        
        # Check if session exists
        query = "SELECT session_id FROM personal_training_sessions WHERE session_id = %s"
        result = self.db.execute_query(query, (session_id,))
        
        if not result:
            QMessageBox.critical(self, "Ошибка", "Сеанс не найден")
            return
        
        # Add exercise
        insert_query = """
        INSERT INTO training_journal (session_id, exercise_name, sets, reps, weight)
        VALUES (%s, %s, %s, %s, %s)
        """
        weight_val = float(weight) if weight else None
        result = self.db.execute_insert(insert_query, (session_id, exercise, sets, reps, weight_val))
        
        if result:
            QMessageBox.information(self, "Успех", "Упражнение добавлено в журнал")
            self.session_id_input.clear()
            self.exercise_input.clear()
            self.sets_input.setValue(1)
            self.reps_input.setValue(1)
            self.weight_input.clear()
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить упражнение")

    def reset_filter(self):
        self.date_filter_input.setDate(QDate.currentDate())
        self.load_sessions(filter_by_date=False)

    def load_sessions(self, filter_by_date=False):
        base_query = """SELECT pts.session_id, CONCAT(c.first_name, ' ', c.last_name), CONCAT(t.first_name, ' ', t.last_name), 
                             pts.session_date, pts.duration_minutes, pts.status, pts.booking_date
                      FROM personal_training_sessions pts
                      JOIN clients c ON pts.client_id = c.client_id
                      JOIN trainers t ON pts.trainer_id = t.trainer_id"""
        params = []
        if filter_by_date:
            selected_date = self.date_filter_input.date().toString('yyyy-MM-dd')
            base_query += " WHERE DATE(pts.session_date) = %s"
            params.append(selected_date)
        
        base_query += " ORDER BY pts.session_date DESC"
        results = self.db.execute_query(base_query, tuple(params))
        
        self.sessions_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.sessions_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.sessions_table.setItem(row_idx, col_idx, item)

    def load_data(self):
        # Load trainers
        query = "SELECT trainer_id, CONCAT(first_name, ' ', last_name) FROM trainers WHERE status = 'active'"
        results = self.db.execute_query(query)
        
        self.trainer_combo.clear()
        if results:
            for trainer_id, trainer_name in results:
                self.trainer_combo.addItem(trainer_name, trainer_id)
        
        # Load sessions
        self.load_sessions(filter_by_date=False)

        # Load journal
        query = """
        SELECT tj.journal_id, tj.session_id, tj.exercise_name, tj.sets, tj.reps, tj.weight, tj.recorded_date
        FROM training_journal tj
        ORDER BY tj.recorded_date DESC
        LIMIT 100
        """
        results = self.db.execute_query(query)
        
        self.journal_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.journal_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.journal_table.setItem(row_idx, col_idx, item)
