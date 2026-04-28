from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .training_program_management import TrainingProgramManagementWidget
from .notifications_widget import NotificationsWidget
from .block_time_dialog import BlockTimeDialog

class TrainerMainWidget(QWidget):
    def __init__(self, db, user_info, logout_callback):
        super().__init__()
        self.db = db
        self.user_info = user_info
        self.logout_callback = logout_callback
        self.setWindowTitle("Fitness Club Management")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Панель тренера")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Занятия тренера
        layout.addWidget(QLabel("Ваши групповые занятия:"))
        self.classes_table = QTableWidget()
        self.classes_table.setColumnCount(5)
        self.classes_table.setHorizontalHeaderLabels(['ID', 'Название', 'Зал', 'Макс участников', 'Длительность'])
        self.classes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.classes_table)

        # Клиенты на занятиях
        layout.addWidget(QLabel("Клиенты на ваших занятиях:"))
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels(['ID', 'Занятие', 'Дата', 'Клиент', 'Статус', 'Дата записи'])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.clients_table)

        attendance_btn = QPushButton("Отметить присутствие")
        attendance_btn.clicked.connect(self.mark_attendance)
        layout.addWidget(attendance_btn)

        # Журнал персональных тренировок
        layout.addWidget(QLabel("Журнал персональных тренировок:"))
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(['ID', 'Клиент', 'Дата', 'Длительность', 'Статус', 'Дата бронирования'])
        self.sessions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sessions_table)

        journal_btn = QPushButton("Вести журнал тренировки")
        journal_btn.clicked.connect(self.open_journal)
        layout.addWidget(journal_btn)

        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.logout_callback)
        layout.addWidget(logout_btn)

        record_progress_btn = QPushButton("Зафиксировать прогресс клиента")
        record_progress_btn.clicked.connect(self.open_record_progress_dialog)
        layout.addWidget(record_progress_btn)

        self.tabs = QTabWidget()
        self.training_program_widget = TrainingProgramManagementWidget(self.db, self.user_info)
        self.notifications_widget = NotificationsWidget(self.db, self.user_info)
        self.tabs.addTab(self.training_program_widget, "Программы тренировок")
        self.tabs.addTab(self.notifications_widget, "Уведомления")
        layout.addWidget(self.tabs)

        # Blocked time
        layout.addWidget(QLabel("Заблокированное время:"))
        self.blocked_time_table = QTableWidget()
        self.blocked_time_table.setColumnCount(4)
        self.blocked_time_table.setHorizontalHeaderLabels(['ID', 'Начало', 'Окончание', 'Причина'])
        self.blocked_time_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.blocked_time_table)

        block_time_btn = QPushButton("Заблокировать время")
        block_time_btn.clicked.connect(self.open_block_time_dialog)
        layout.addWidget(block_time_btn)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        trainer_id = self.user_info.get('trainer_id')
        # Загрузить групповые занятия тренера
        query = '''SELECT class_id, name, room_number, max_participants, duration_minutes FROM group_classes WHERE trainer_id = %s'''
        results = self.db.execute_query(query, (trainer_id,))
        self.classes_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.classes_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.classes_table.setItem(row_idx, col_idx, item)
        # Клиенты на занятиях
        query = '''SELECT ce.enrollment_id, gc.name, ce.class_date, CONCAT(c.first_name, ' ', c.last_name), ce.attendance_status, ce.enrollment_date
                   FROM class_enrollments ce
                   JOIN class_schedule cs ON ce.schedule_id = cs.schedule_id
                   JOIN group_classes gc ON cs.class_id = gc.class_id
                   JOIN clients c ON ce.client_id = c.client_id
                   WHERE gc.trainer_id = %s
                   ORDER BY ce.class_date DESC'''
        results = self.db.execute_query(query, (trainer_id,))
        self.clients_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.clients_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.clients_table.setItem(row_idx, col_idx, item)
        # Журнал персональных тренировок
        query = '''SELECT pts.session_id, CONCAT(c.first_name, ' ', c.last_name), pts.session_date, pts.duration_minutes, pts.status, pts.booking_date FROM personal_training_sessions pts JOIN clients c ON pts.client_id = c.client_id WHERE pts.trainer_id = %s ORDER BY pts.session_date DESC'''
        results = self.db.execute_query(query, (trainer_id,))
        self.sessions_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.sessions_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.sessions_table.setItem(row_idx, col_idx, item)

        # Заблокированное время
        query = '''SELECT availability_id, start_time, end_time, reason FROM trainer_availability WHERE trainer_id = %s ORDER BY start_time DESC'''
        results = self.db.execute_query(query, (trainer_id,))
        self.blocked_time_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.blocked_time_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "")
                    self.blocked_time_table.setItem(row_idx, col_idx, item)
        self.notifications_widget.load_notifications()

    def mark_attendance(self):
        selected_items = self.clients_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для отметки присутствия.")
            return
        
        enrollment_id = self.clients_table.item(selected_items[0].row(), 0).text()
        query = "UPDATE class_enrollments SET attendance_status = 'attended' WHERE enrollment_id = %s"
        rows_affected = self.db.execute_update(query, (enrollment_id,))
        if rows_affected > 0:
            QMessageBox.information(self, "Успех", "Присутствие отмечено.")
            self.load_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось отметить присутствие.")

    def open_journal(self):
        selected_items = self.sessions_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите персональную тренировку для ведения журнала.")
            return
        
        session_id = self.sessions_table.item(selected_items[0].row(), 0).text()
        from .training_journal_dialog import TrainingJournalDialog
        dlg = TrainingJournalDialog(self.db, session_id, self.load_data)
        dlg.exec()

    def open_record_progress_dialog(self):
        from .record_progress_dialog import RecordProgressDialog
        # We need trainer_id to find their clients
        trainer_id = self.user_info.get('trainer_id')
        dlg = RecordProgressDialog(self.db, trainer_id, self.load_data) # Assuming load_data is a sufficient callback
        dlg.exec()

    def open_block_time_dialog(self):
        from .block_time_dialog import BlockTimeDialog
        trainer_id = self.user_info.get('trainer_id')
        dlg = BlockTimeDialog(self.db, trainer_id, self.load_data)
        dlg.exec()
