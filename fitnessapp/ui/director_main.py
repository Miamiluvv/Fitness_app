from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt6.QtGui import QFont
from .reports import ReportsWidget
from .notifications_widget import NotificationsWidget
from .financial_report import FinancialReportWidget

class DirectorMainWidget(QWidget):
    def __init__(self, db, user_info, logout_callback):
        super().__init__()
        self.db = db
        self.user_info = user_info
        self.logout_callback = logout_callback
        self.setWindowTitle("Fitness Club Management")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Панель Управления Директора")
        title.setFont(QFont('Segoe UI', 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # Tabs for different reports
        self.tabs = QTabWidget()
        
        # Reports widget (reusing) but could be a custom dashboard
        self.reports_widget = ReportsWidget(self.db)
        self.notifications_widget = NotificationsWidget(self.db, self.user_info)
        self.financial_report = FinancialReportWidget(self.db)

        self.tabs.addTab(self.reports_widget, "Отчеты")
        self.tabs.addTab(self.notifications_widget, "Уведомления")
        self.tabs.addTab(self.financial_report, "Финансовый отчет")

        layout.addWidget(self.tabs)

        logout_btn = QPushButton("Выйти")
        logout_btn.clicked.connect(self.logout_callback)
        layout.addWidget(logout_btn)

        self.setLayout(layout)
