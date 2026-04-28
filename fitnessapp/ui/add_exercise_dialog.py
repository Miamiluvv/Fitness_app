from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTextEdit, QSpinBox

class AddExerciseDialog(QDialog):
    def __init__(self, db, program_id, on_success):
        super().__init__()
        self.db = db
        self.program_id = program_id
        self.on_success = on_success
        self.setWindowTitle("Добавить упражнение")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Название упражнения:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Сеты:"))
        self.sets_input = QSpinBox()
        self.sets_input.setRange(1, 20)
        layout.addWidget(self.sets_input)

        layout.addWidget(QLabel("Повторения:"))
        self.reps_input = QLineEdit() # Using QLineEdit for flexibility like '8-12'
        layout.addWidget(self.reps_input)

        layout.addWidget(QLabel("Заметки:"))
        self.notes_input = QTextEdit()
        layout.addWidget(self.notes_input)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_exercise)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_exercise(self):
        name = self.name_input.text()
        sets = self.sets_input.value()
        reps = self.reps_input.text()
        notes = self.notes_input.toPlainText()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название упражнения.")
            return

        query = "INSERT INTO program_exercises (program_id, exercise_name, sets, reps, notes) VALUES (%s, %s, %s, %s, %s)"
        params = (self.program_id, name, sets, reps, notes)
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", "Упражнение добавлено.")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить упражнение.")
