from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTextEdit, QMessageBox

class TrainingJournalDialog(QDialog):
    def __init__(self, db, session_id, on_success):
        super().__init__()
        self.db = db
        self.session_id = session_id
        self.on_success = on_success
        self.setWindowTitle("Добавить запись в журнал")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Упражнение:"))
        self.exercise_input = QLineEdit()
        layout.addWidget(self.exercise_input)

        layout.addWidget(QLabel("Подходы:"))
        self.sets_input = QSpinBox()
        self.sets_input.setRange(1, 20)
        layout.addWidget(self.sets_input)

        layout.addWidget(QLabel("Повторения:"))
        self.reps_input = QSpinBox()
        self.reps_input.setRange(1, 100)
        layout.addWidget(self.reps_input)

        layout.addWidget(QLabel("Вес:"))
        self.weight_input = QLineEdit()
        layout.addWidget(self.weight_input)

        layout.addWidget(QLabel("Заметки:"))
        self.notes_input = QTextEdit()
        layout.addWidget(self.notes_input)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_entry)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def save_entry(self):
        exercise = self.exercise_input.text()
        sets = self.sets_input.value()
        reps = self.reps_input.value()
        weight = self.weight_input.text()
        notes = self.notes_input.toPlainText()

        if not exercise:
            QMessageBox.warning(self, "Ошибка", "Введите название упражнения.")
            return

        query = "INSERT INTO training_journal (session_id, exercise_name, sets, reps, weight, notes) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (self.session_id, exercise, sets, reps, weight if weight else None, notes)
        result = self.db.execute_insert(query, params)
        if result:
            QMessageBox.information(self, "Успех", "Запись добавлена в журнал.")
            self.on_success()
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось добавить запись.")
