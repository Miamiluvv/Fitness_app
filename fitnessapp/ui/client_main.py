from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .client_schedule import ClientScheduleWidget
from .client_progress import ClientProgressWidget
from .notifications_widget import NotificationsWidget

class ClientMainWidget(QWidget):
    def __init__(self, db, user_info, logout_callback):
        super().__init__()
        self.db = db
        self.user_info = user_info
        self.logout_callback = logout_callback
        self.setWindowTitle("Fitness Club Management")
        self.init_ui()

    def init_ui(self):
        try:
            layout = QVBoxLayout()
            title = QLabel("Личный кабинет клиента")
            title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
            layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

            # Tab widget
            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)

            # Main Tab (Memberships & Attendance)
            main_tab = QWidget()
            main_layout = QVBoxLayout()
            main_tab.setLayout(main_layout)

            main_layout.addWidget(QLabel("Ваши абонементы:"))
            self.memberships_table = QTableWidget()
            self.memberships_table.setColumnCount(6)
            self.memberships_table.setHorizontalHeaderLabels(['ID', 'Тип', 'Начало', 'Окончание', 'Статус', 'Осталось'])
            self.memberships_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            main_layout.addWidget(self.memberships_table)

            main_layout.addWidget(QLabel("Ваши посещения:"))
            self.attendance_table = QTableWidget()
            self.attendance_table.setColumnCount(5)
            self.attendance_table.setHorizontalHeaderLabels(['ID', 'Вход', 'Выход', 'Зона', 'Длительность'])
            self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            main_layout.addWidget(self.attendance_table)

            buy_btn = QPushButton("Купить абонемент")
            buy_btn.clicked.connect(self.buy_membership)
            main_layout.addWidget(buy_btn)

            enroll_btn = QPushButton("Записаться на групповое занятие")
            enroll_btn.clicked.connect(self.enroll_class)
            main_layout.addWidget(enroll_btn)

            book_training_btn = QPushButton("Записаться на персональную тренировку")
            book_training_btn.clicked.connect(self.book_training)
            main_layout.addWidget(book_training_btn)

            logout_btn = QPushButton("Выйти")
            logout_btn.clicked.connect(self.logout_callback)
            main_layout.addWidget(logout_btn)

            # Schedule and Progress Tabs
            self.schedule_widget = ClientScheduleWidget(self.db, self.user_info['client_id'])
            self.progress_widget = ClientProgressWidget(self.db, self.user_info)
            self.notifications_widget = NotificationsWidget(self.db, self.user_info)

            self.tabs.addTab(main_tab, "Абонементы и Посещения")
            self.tabs.addTab(self.schedule_widget, "Расписание и Запись")
            self.tabs.addTab(self.progress_widget, "Мой Прогресс")
            self.tabs.addTab(self.notifications_widget, "Уведомления")

            self.setLayout(layout)
            self.refresh_all_data()
        except Exception as e:
            print(f"ClientMainWidget init_ui error: {e}")

    def load_data(self):
        try:
            client_id = self.user_info.get('client_id')
            # Абонементы
            query = '''SELECT m.membership_id, mt.name, m.start_date, m.end_date, m.status, m.visits_remaining FROM memberships m JOIN membership_types mt ON m.membership_type_id = mt.membership_type_id WHERE m.client_id = %s'''
            results = self.db.execute_query(query, (client_id,))
            self.memberships_table.setRowCount(0)

            status_translation = {
                'active': 'Активен',
                'expired': 'Истек',
                'cancelled': 'Отменен',
                'frozen': 'Заморожен'
            }

            if results:
                for row_idx, row_data in enumerate(results):
                    self.memberships_table.insertRow(row_idx)
                    # id, type, start, end
                    for col_idx in range(4):
                        value = row_data[col_idx]
                        item = QTableWidgetItem(str(value) if value else "")
                        self.memberships_table.setItem(row_idx, col_idx, item)

                    # Status
                    status_en = row_data[4]
                    status_ru = status_translation.get(status_en, status_en)
                    self.memberships_table.setItem(row_idx, 4, QTableWidgetItem(status_ru))

                    # Remaining
                    end_date = row_data[3]
                    visits_remaining = row_data[5]
                    remaining_text = ""
                    if visits_remaining is not None:
                        remaining_text = f"{visits_remaining} посещений"
                    elif end_date:
                        from datetime import date
                        remaining_days = (end_date - date.today()).days
                        if remaining_days >= 0:
                            remaining_text = f"{remaining_days} дней"
                        else:
                            remaining_text = "Истек"
                    self.memberships_table.setItem(row_idx, 5, QTableWidgetItem(remaining_text))

            # Посещения
            query = '''SELECT attendance_id, check_in_time, check_out_time, zone_accessed, TIMEDIFF(check_out_time, check_in_time) FROM attendance WHERE client_id = %s'''
            results = self.db.execute_query(query, (client_id,))
            self.attendance_table.setRowCount(0)
            if results:
                for row_idx, row_data in enumerate(results):
                    self.attendance_table.insertRow(row_idx)
                    for col_idx, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value) if value else "")
                        self.attendance_table.setItem(row_idx, col_idx, item)
        except Exception as e:
            print(f"ClientMainWidget load_data error: {e}")

    def refresh_all_data(self):
        self.load_data()
        self.schedule_widget.load_enrollments()
        self.progress_widget.load_progress()
        self.notifications_widget.load_notifications()

    def buy_membership(self):
        try:
            from ui.buy_membership_dialog import BuyMembershipDialog
            dlg = BuyMembershipDialog(self.db, self.user_info.get('client_id'), self.refresh_all_data)
            dlg.exec()
        except Exception as e:
            print(f"ClientMainWidget buy_membership error: {e}")

    def enroll_class(self):
        try:
            from ui.enroll_class_dialog import EnrollClassDialog
            dlg = EnrollClassDialog(self.db, self.user_info.get('client_id'), self.refresh_all_data)
            dlg.exec()
        except Exception as e:
            print(f"ClientMainWidget enroll_class error: {e}")

    def book_training(self):
        try:
            from ui.book_training_dialog import BookTrainingDialog
            dlg = BookTrainingDialog(self.db, self.user_info.get('client_id'), self.refresh_all_data)
            dlg.exec()
        except Exception as e:
            print(f"ClientMainWidget book_training error: {e}")
