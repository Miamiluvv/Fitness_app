from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QMessageBox, QHeaderView, QTimeEdit, QSpinBox)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont

class ClassScheduleWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Управление расписанием занятий")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Create class section
        create_layout = QHBoxLayout()
        
        create_layout.addWidget(QLabel("Название занятия:"))
        self.class_name_input = QLineEdit()
        create_layout.addWidget(self.class_name_input)
        
        create_layout.addWidget(QLabel("Тренер:"))
        self.trainer_combo = QComboBox()
        create_layout.addWidget(self.trainer_combo)
        
        create_layout.addWidget(QLabel("Зал:"))
        self.room_input = QSpinBox()
        self.room_input.setMinimum(1)
        self.room_input.setMaximum(20)
        create_layout.addWidget(self.room_input)
        
        create_layout.addWidget(QLabel("Макс участников:"))
        self.max_participants_input = QSpinBox()
        self.max_participants_input.setMinimum(1)
        self.max_participants_input.setMaximum(100)
        self.max_participants_input.setValue(20)
        create_layout.addWidget(self.max_participants_input)
        
        create_layout.addWidget(QLabel("Длительность (мин):"))
        self.duration_input = QSpinBox()
        self.duration_input.setMinimum(15)
        self.duration_input.setMaximum(180)
        self.duration_input.setValue(60)
        create_layout.addWidget(self.duration_input)
        
        create_btn = QPushButton("Создать занятие")
        create_btn.clicked.connect(self.create_class)
        create_layout.addWidget(create_btn)
        
        layout.addLayout(create_layout)
        
        # Classes list
        layout.addWidget(QLabel("Доступные занятия:"))
        self.classes_table = QTableWidget()
        self.classes_table.setColumnCount(6)
        self.classes_table.setHorizontalHeaderLabels(['ID', 'Название', 'Тренер', 'Зал', 'Макс участников', 'Длительность'])
        self.classes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.classes_table)
        
        # Schedule section
        schedule_layout = QHBoxLayout()
        
        schedule_layout.addWidget(QLabel("Занятие:"))
        self.class_combo = QComboBox()
        schedule_layout.addWidget(self.class_combo)
        
        schedule_layout.addWidget(QLabel("День:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'])
        schedule_layout.addWidget(self.day_combo)
        
        schedule_layout.addWidget(QLabel("Время начала:"))
        self.start_time_input = QTimeEdit()
        self.start_time_input.setTime(QTime(10, 0))
        schedule_layout.addWidget(self.start_time_input)
        
        schedule_btn = QPushButton("Добавить расписание")
        schedule_btn.clicked.connect(self.add_schedule)
        schedule_layout.addWidget(schedule_btn)
        
        layout.addLayout(schedule_layout)
        
        # Schedule list
        layout.addWidget(QLabel("Расписание занятий:"))
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(6)
        self.schedule_table.setHorizontalHeaderLabels(['ID расписания', 'Занятие', 'День', 'Начало', 'Конец', 'Тренер'])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.schedule_table)
        
        # Refresh button
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_data()

    def create_class(self):
        class_name = self.class_name_input.text()
        trainer_id = self.trainer_combo.currentData()
        room = self.room_input.value()
        max_participants = self.max_participants_input.value()
        duration = self.duration_input.value()
        
        if not class_name or not trainer_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, заполните все поля")
            return
        
        query = """
        INSERT INTO group_classes (name, trainer_id, room_number, max_participants, duration_minutes)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (class_name, trainer_id, room, max_participants, duration)
        
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", f"Занятие создано с ID: {result}")
            self.class_name_input.clear()
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось создать занятие")

    def add_schedule(self):
        class_id = self.class_combo.currentData()
        day = self.day_combo.currentText()
        start_time = self.start_time_input.time().toString('HH:mm:ss')
        
        # Map Russian day names to English
        day_map = {'Понедельник': 'Monday', 'Вторник': 'Tuesday', 'Среда': 'Wednesday', 
                   'Четверг': 'Thursday', 'Пятница': 'Friday', 'Суббота': 'Saturday', 'Воскресенье': 'Sunday'}
        day_db = day_map.get(day, day)
        
        if not class_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, выберите занятие")
            return
        
        # Get class duration
        query = "SELECT duration_minutes FROM group_classes WHERE class_id = %s"
        result = self.db.execute_query(query, (class_id,))
        
        if not result:
            QMessageBox.critical(self, "Ошибка", "Занятие не найдено")
            return
        
        duration = result[0][0]
        
        # Calculate end time
        start_qtime = self.start_time_input.time()
        end_qtime = start_qtime.addSecs(duration * 60)
        end_time = end_qtime.toString('HH:mm:ss')
        
        insert_query = """
        INSERT INTO class_schedule (class_id, day_of_week, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """
        params = (class_id, day_db, start_time, end_time)
        
        result = self.db.execute_insert(insert_query, params)
        if result:
            QMessageBox.information(self, "Успех", "Расписание добавлено")
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить расписание")

    def load_data(self):
        # Load trainers
        query = "SELECT trainer_id, CONCAT(first_name, ' ', last_name) FROM trainers WHERE status = 'active'"
        results = self.db.execute_query(query)
        
        self.trainer_combo.clear()
        self.class_combo.clear()
        
        if results:
            for trainer_id, trainer_name in results:
                self.trainer_combo.addItem(trainer_name, trainer_id)
        
        # Load classes
        query = """
        SELECT gc.class_id, gc.name, CONCAT(t.first_name, ' ', t.last_name), 
               gc.room_number, gc.max_participants, gc.duration_minutes
        FROM group_classes gc
        JOIN trainers t ON gc.trainer_id = t.trainer_id
        """
        results = self.db.execute_query(query)
        
        self.classes_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.classes_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.classes_table.setItem(row_idx, col_idx, item)
                
                self.class_combo.addItem(row_data[1], row_data[0])
        
        # Load schedule
        query = """
        SELECT cs.schedule_id, gc.name, cs.day_of_week, cs.start_time, cs.end_time,
               CONCAT(t.first_name, ' ', t.last_name)
        FROM class_schedule cs
        JOIN group_classes gc ON cs.class_id = gc.class_id
        JOIN trainers t ON gc.trainer_id = t.trainer_id
        ORDER BY FIELD(cs.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
                 cs.start_time
        """
        results = self.db.execute_query(query)
        
        self.schedule_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.schedule_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.schedule_table.setItem(row_idx, col_idx, item)
