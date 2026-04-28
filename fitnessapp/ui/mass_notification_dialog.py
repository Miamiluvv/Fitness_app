from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox

class MassNotificationDialog(QDialog):
    def __init__(self, db, notifier):
        super().__init__()
        self.db = db
        self.notifier = notifier
        self.setWindowTitle("Массовая Рассылка Уведомлений")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Тема:"))
        self.subject_input = QLineEdit()
        layout.addWidget(self.subject_input)

        layout.addWidget(QLabel("Сообщение:"))
        self.body_input = QTextEdit()
        layout.addWidget(self.body_input)

        send_btn = QPushButton("Отправить всем активным клиентам")
        send_btn.clicked.connect(self.send_notifications)
        layout.addWidget(send_btn)
        self.setLayout(layout)

    def send_notifications(self):
        subject = self.subject_input.text()
        body = self.body_input.toPlainText()

        if not subject or not body:
            QMessageBox.warning(self, "Ошибка", "Введите тему и текст сообщения.")
            return

        query = "SELECT u.user_id FROM users u JOIN clients c ON u.client_id = c.client_id WHERE c.status = 'active'"
        results = self.db.execute_query(query)
        if not results:
            QMessageBox.information(self, "Информация", "Нет активных клиентов для рассылки.")
            return

        user_ids = [row[0] for row in results]
        insert_query = "INSERT INTO notifications (user_id, subject, body) VALUES (%s, %s, %s)"
        
        count = 0
        for user_id in user_ids:
            try:
                self.db.execute_insert(insert_query, (user_id, subject, body))
                count += 1
            except Exception as e:
                print(f"Could not send notification to user {user_id}: {e}")

        QMessageBox.information(self, "Успех", f"Уведомления отправлены {count} клиентам.")
        self.accept()
