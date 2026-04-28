import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel, QStyle)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from database import DatabaseConnection
from ui.client_registration import ClientRegistrationWidget
from ui.membership_management import MembershipManagementWidget
from ui.attendance_tracking import AttendanceTrackingWidget
from ui.class_schedule import ClassScheduleWidget
from ui.class_enrollment import ClassEnrollmentWidget
from ui.personal_training import PersonalTrainingWidget
from ui.reports import ReportsWidget
from ui.feedback_management import FeedbackManagementWidget
from ui.user_management import UserManagementWidget
from ui.promotions_management import PromotionsManagementWidget
from ui.mass_notification_dialog import MassNotificationDialog

class FitnessClubApp(QMainWindow):
    def __init__(self, db, logout_callback):
        super().__init__()
        self.db = db
        self.logout_callback = logout_callback
        self.init_ui()
        self.setup_notifications()

    def init_ui(self):
        self.setWindowTitle("Fitness Club Management")
        self.setGeometry(100, 100, 1400, 900)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout()
        
        # Sidebar with navigation buttons
        sidebar = self.create_sidebar()
        layout.addWidget(sidebar)
        
        # Main content area
        self.stacked_widget = QStackedWidget()
        self.setup_pages()
        layout.addWidget(self.stacked_widget, 1)
        
        main_widget.setLayout(layout)

    def create_sidebar(self):
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Фитнес Клуб")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        sidebar_layout.addWidget(title)
        
        # Navigation buttons
        buttons_info = [
            ("Клиенты", 0, QStyle.StandardPixmap.SP_DirIcon),
            ("Абонементы", 1, QStyle.StandardPixmap.SP_FileIcon),
            ("Посещения", 2, QStyle.StandardPixmap.SP_ComputerIcon),
            ("Занятия", 3, QStyle.StandardPixmap.SP_DesktopIcon),
            ("Запись на занятия", 4, QStyle.StandardPixmap.SP_DialogApplyButton),
            ("Персональные тренировки", 5, QStyle.StandardPixmap.SP_DialogYesButton),
            ("Отчеты", 6, QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ("Обратная связь", 7, QStyle.StandardPixmap.SP_MessageBoxInformation),
            ("Акции", 8, QStyle.StandardPixmap.SP_DialogHelpButton)
        ]

        style = self.style()
        for button_text, page_index, icon_pixmap in buttons_info:
            icon = style.standardIcon(icon_pixmap)
            btn = QPushButton(icon, f' {button_text}')
            btn.setIconSize(QSize(24, 24))
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, idx=page_index: self.stacked_widget.setCurrentIndex(idx))
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        notification_btn = QPushButton("Массовые уведомления")
        notification_btn.clicked.connect(self.open_mass_notification_dialog)
        sidebar_layout.addWidget(notification_btn)

        logout_btn = QPushButton("Выйти")
        logout_btn.setMinimumHeight(50)
        logout_btn.clicked.connect(self.logout_callback)
        sidebar_layout.addWidget(logout_btn)
        
        sidebar_widget.setObjectName("sidebar_widget")
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(200)
        return sidebar_widget

    def setup_pages(self):
        self.stacked_widget.addWidget(ClientRegistrationWidget(self.db))
        self.stacked_widget.addWidget(MembershipManagementWidget(self.db))
        self.stacked_widget.addWidget(AttendanceTrackingWidget(self.db))
        self.stacked_widget.addWidget(ClassScheduleWidget(self.db))
        self.stacked_widget.addWidget(ClassEnrollmentWidget(self.db))
        self.stacked_widget.addWidget(PersonalTrainingWidget(self.db))
        self.stacked_widget.addWidget(ReportsWidget(self.db))
        self.feedback_widget = FeedbackManagementWidget(self.db)
        self.user_management_widget = UserManagementWidget(self.db)
        self.stacked_widget.addWidget(self.feedback_widget)
        self.stacked_widget.addWidget(self.user_management_widget)
        self.stacked_widget.addWidget(PromotionsManagementWidget(self.db))

    def open_mass_notification_dialog(self):
        # Notifier is currently disabled in setup_notifications, so we pass None
        dlg = MassNotificationDialog(self.db, None)
        dlg.exec()

    def setup_notifications(self):
        # This is a placeholder for a real implementation.
        # In a real app, you would configure SMTP settings securely.
        # self.notifier = EmailNotifier('smtp.example.com', 465, 'user', 'pass')
        
        # Timer to check for upcoming sessions
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.check_upcoming_sessions)
        self.notification_timer.start(3600000) # Check every hour

    def check_upcoming_sessions(self):
        print("Checking for upcoming sessions...")
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        query = """SELECT u.user_id, pts.session_date
                   FROM personal_training_sessions pts
                   JOIN clients c ON pts.client_id = c.client_id
                   JOIN users u ON c.client_id = u.client_id
                   WHERE DATE(pts.session_date) = %s AND pts.status = 'scheduled'"""
        sessions = self.db.execute_query(query, (tomorrow,))
        if sessions:
            for user_id, session_date in sessions:
                subject = "Напоминание о тренировке"
                body = f"Напоминаем, что у вас запланирована персональная тренировка на {session_date}."
                insert_query = "INSERT INTO notifications (user_id, subject, body) VALUES (%s, %s, %s)"
                self.db.execute_insert(insert_query, (user_id, subject, body))

    def close_app(self):
        self.db.disconnect()
        self.close()

from ui.login import LoginWidget
from ui.notifications import EmailNotifier
from PyQt6.QtCore import QTimer
import datetime

class AppController:
    def __init__(self, app):
        self.app = app
        self.db = DatabaseConnection()
        self.db.connect()
        self.current_window = None

    def show_login(self):
        if self.current_window:
            self.current_window.close()
        self.login_widget = LoginWidget(self.db, self.on_login)
        self.current_window = self.login_widget
        self.current_window.show()

    def on_login(self, user_info):
        role = user_info['role']
        self.login_widget.hide()

        if role == 'admin':
            self.current_window = FitnessClubApp(self.db, self.show_login)
        elif role == 'trainer':
            from ui.trainer_main import TrainerMainWidget
            self.current_window = TrainerMainWidget(self.db, user_info, self.show_login)
        elif role == 'client':
            from ui.client_main import ClientMainWidget
            self.current_window = ClientMainWidget(self.db, user_info, self.show_login)
        elif role == 'director':
            from ui.director_main import DirectorMainWidget
            self.current_window = DirectorMainWidget(self.db, user_info, self.show_login)
        
        if self.current_window:
            self.current_window.show()
        else:
            QMessageBox.critical(None, "Ошибка", "Неизвестная роль пользователя")
            self.show_login()

def main():
    app = QApplication(sys.argv)
    # Apply global stylesheet
    with open('style.qss', 'r') as f:
        app.setStyleSheet(f.read())
    
    controller = AppController(app)
    controller.show_login()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
