from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView
from PyQt6.QtGui import QFont

class NotificationsWidget(QWidget):
    def __init__(self, db, user_info):
        super().__init__()
        self.db = db
        self.user_info = user_info
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Уведомления")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.notifications_table = QTableWidget()
        self.notifications_table.setColumnCount(4)
        self.notifications_table.setHorizontalHeaderLabels(['ID', 'Тема', 'Сообщение', 'Дата'])
        self.notifications_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.notifications_table.setColumnHidden(0, True) # Hide ID column
        layout.addWidget(self.notifications_table)

        self.mark_read_button = QPushButton("Отметить как прочитанное")
        self.mark_read_button.clicked.connect(self.mark_as_read)
        layout.addWidget(self.mark_read_button)

        self.setLayout(layout)
        self.load_notifications()

    def load_notifications(self):
        user_id = self.user_info.get('user_id')
        if not user_id:
            return

        query = "SELECT notification_id, subject, body, created_at FROM notifications WHERE user_id = %s AND is_read = FALSE ORDER BY created_at DESC"
        results = self.db.execute_query(query, (user_id,))
        self.notifications_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.notifications_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.notifications_table.setItem(row_idx, col_idx, item)

    def mark_as_read(self):
        selected_items = self.notifications_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите уведомление для отметки.")
            return

        selected_row = self.notifications_table.row(selected_items[0])
        notification_id = self.notifications_table.item(selected_row, 0).text()

        query = "UPDATE notifications SET is_read = TRUE WHERE notification_id = %s"
        rows_affected = self.db.execute_update(query, (notification_id,))
        if rows_affected > 0:
            self.load_notifications() # Refresh the list
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось обновить статус уведомления.")
