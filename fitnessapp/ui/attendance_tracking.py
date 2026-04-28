from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
                             QMessageBox, QHeaderView, QDateEdit)
from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtGui import QFont

class AttendanceTrackingWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Учет посещений")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Check-in/Check-out section
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("ID клиента:"))
        self.client_id_input = QLineEdit()
        control_layout.addWidget(self.client_id_input)
        
        control_layout.addWidget(QLabel("Зона:"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(['Тренажерный зал', 'Бассейн', 'Групповые занятия'])
        control_layout.addWidget(self.zone_combo)
        
        checkin_btn = QPushButton("Вход")
        checkin_btn.clicked.connect(self.check_in)
        control_layout.addWidget(checkin_btn)
        
        checkout_btn = QPushButton("Выход")
        checkout_btn.clicked.connect(self.check_out)
        control_layout.addWidget(checkout_btn)
        
        layout.addLayout(control_layout)
        
        # Today's attendance
        layout.addWidget(QLabel("Посещения за день:"))
        self.today_table = QTableWidget()
        self.today_table.setColumnCount(6)
        self.today_table.setHorizontalHeaderLabels(['ID посещения', 'ID клиента', 'Вход', 'Выход', 'Зона', 'Длительность'])
        self.today_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.today_table)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Фильтр по дате:"))
        self.filter_date = QDateEdit()
        self.filter_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.filter_date)
        
        filter_btn = QPushButton("Применить фильтр")
        filter_btn.clicked.connect(self.load_attendance)
        filter_layout.addWidget(filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Refresh button
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_attendance)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        self.load_attendance()

    def check_in(self):
        client_id = self.client_id_input.text()
        zone = self.zone_combo.currentText()
        
        # Map Russian zone names to database values
        zone_map = {'Тренажерный зал': 'gym', 'Бассейн': 'pool', 'Групповые занятия': 'group_classes'}
        zone_db = zone_map.get(zone, zone)
        
        if not client_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, введите ID клиента")
            return
        
        # Check if client has active membership
        query = """
        SELECT membership_id FROM memberships 
        WHERE client_id = %s AND status = 'active' AND end_date >= CURDATE()
        LIMIT 1
        """
        result = self.db.execute_query(query, (client_id,))
        
        if not result:
            QMessageBox.critical(self, "Ошибка", "У клиента нет активного абонемента")
            return
        
        membership_id = result[0][0]
        
        # Record check-in
        insert_query = """
        INSERT INTO attendance (client_id, membership_id, check_in_time, zone_accessed)
        VALUES (%s, %s, NOW(), %s)
        """
        result = self.db.execute_insert(insert_query, (client_id, membership_id, zone_db))
        
        if result:
            QMessageBox.information(self, "Успех", f"Клиент {client_id} вошел")
            self.client_id_input.clear()
            self.load_attendance()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось записать вход")

    def check_out(self):
        client_id = self.client_id_input.text()
        
        if not client_id:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, введите ID клиента")
            return
        
        # Find latest check-in without check-out
        query = """
        SELECT attendance_id FROM attendance 
        WHERE client_id = %s AND check_out_time IS NULL
        ORDER BY check_in_time DESC
        LIMIT 1
        """
        result = self.db.execute_query(query, (client_id,))
        
        if not result:
            QMessageBox.critical(self, "Ошибка", "Нет активного входа для этого клиента")
            return
        
        attendance_id = result[0][0]
        
        # Record check-out
        update_query = """
        UPDATE attendance SET check_out_time = NOW() WHERE attendance_id = %s
        """
        self.db.execute_update(update_query, (attendance_id,))
        
        QMessageBox.information(self, "Успех", f"Клиент {client_id} вышел")
        self.client_id_input.clear()
        self.load_attendance()

    def load_attendance(self):
        filter_date = self.filter_date.date().toString('yyyy-MM-dd')
        
        query = """
        SELECT attendance_id, client_id, check_in_time, check_out_time, zone_accessed,
               TIMEDIFF(check_out_time, check_in_time) as duration
        FROM attendance
        WHERE DATE(check_in_time) = %s
        ORDER BY check_in_time DESC
        """
        results = self.db.execute_query(query, (filter_date,))
        
        self.today_table.setRowCount(0)
        if results:
            zone_map = {
                'gym': 'Тренажерный зал',
                'pool': 'Бассейн',
                'group_classes': 'Групповые занятия'
            }
            for row_idx, row_data in enumerate(results):
                self.today_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    if col_idx == 4:
                        value = zone_map.get(value, value)
                    item = QTableWidgetItem(str(value) if value else "")
                    self.today_table.setItem(row_idx, col_idx, item)
