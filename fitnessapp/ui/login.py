from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import hashlib

class LoginWidget(QWidget):
    def __init__(self, db, on_login_success):
        super().__init__()
        self.db = db
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Вход в систему")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Пароль")
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.try_login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def try_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        query = "SELECT user_id, password, role, trainer_id, client_id FROM users WHERE username = %s"
        result = self.db.execute_query(query, (username,))
        if not result:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
            return
        user_id, password_db, role, trainer_id, client_id = result[0]
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        if password_md5 == password_db:
            self.on_login_success({
                'user_id': user_id,
                'username': username,
                'role': role,
                'trainer_id': trainer_id,
                'client_id': client_id
            })
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный пароль")
