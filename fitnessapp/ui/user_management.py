from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView
from PyQt6.QtGui import QFont

class UserManagementWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Управление пользователями")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Имя пользователя', 'Роль', 'ID клиента/тренера'])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.users_table)

        self.delete_button = QPushButton("Удалить пользователя")
        self.delete_button.clicked.connect(self.delete_user)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        query = "SELECT user_id, username, role, CONCAT(IFNULL(client_id, ''), IFNULL(trainer_id, '')) FROM users"
        results = self.db.execute_query(query)
        self.users_table.setRowCount(0)
        if results:
            for row_idx, row_data in enumerate(results):
                self.users_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.users_table.setItem(row_idx, col_idx, item)

    def delete_user(self):
        selected_items = self.users_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления.")
            return

        user_id = selected_items[0].text()
        reply = QMessageBox.question(self, 'Подтверждение',
                                     f'Вы уверены, что хотите удалить пользователя с ID {user_id}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            query = "DELETE FROM users WHERE user_id = %s"
            rows_affected = self.db.execute_update(query, (user_id,))
            if rows_affected > 0:
                QMessageBox.information(self, "Успех", "Пользователь успешно удален.")
                self.load_users()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить пользователя.")
