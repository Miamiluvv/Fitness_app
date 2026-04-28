from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QTextEdit, QComboBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QDate
from .add_exercise_dialog import AddExerciseDialog

class TrainingProgramManagementWidget(QWidget):
    def __init__(self, db, trainer_id):
        super().__init__()
        self.db = db
        self.trainer_id = trainer_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Управление Программами Тренировок")
        title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Main layout with two columns
        main_layout = QHBoxLayout()

        # Left column: Programs list and creation
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Мои программы:"))
        self.programs_table = QTableWidget()
        self.programs_table.setColumnCount(2)
        self.programs_table.setHorizontalHeaderLabels(['ID', 'Название'])
        self.programs_table.itemSelectionChanged.connect(self.load_exercises_for_selected_program)
        left_layout.addWidget(self.programs_table)

        left_layout.addWidget(QLabel("Название новой программы:"))
        self.program_name_input = QLineEdit()
        left_layout.addWidget(self.program_name_input)
        left_layout.addWidget(QLabel("Описание:"))
        self.program_desc_input = QTextEdit()
        left_layout.addWidget(self.program_desc_input)
        add_program_btn = QPushButton("Создать программу")
        add_program_btn.clicked.connect(self.create_program)
        left_layout.addWidget(add_program_btn)

        # Right column: Exercises and client assignment
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Упражнения в программе:"))
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(4)
        self.exercises_table.setHorizontalHeaderLabels(['Упражнение', 'Сеты', 'Повторения', 'Заметки'])
        right_layout.addWidget(self.exercises_table)

        add_exercise_btn = QPushButton("Добавить упражнение")
        add_exercise_btn.clicked.connect(self.open_add_exercise_dialog)
        right_layout.addWidget(add_exercise_btn)

        # Assign to client
        assign_layout = QHBoxLayout()
        assign_layout.addWidget(QLabel("Назначить клиенту:"))
        self.client_combo = QComboBox()
        assign_layout.addWidget(self.client_combo)
        assign_btn = QPushButton("Назначить")
        assign_btn.clicked.connect(self.assign_program)
        assign_layout.addWidget(assign_btn)
        right_layout.addLayout(assign_layout)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        layout.addLayout(main_layout)

        self.setLayout(layout)
        self.load_programs()
        self.load_clients()

    def load_programs(self):
        query = "SELECT program_id, name FROM training_programs WHERE trainer_id = %s"
        results = self.db.execute_query(query, (self.trainer_id,))
        self.programs_table.setRowCount(0)
        if results:
            for row, data in enumerate(results):
                self.programs_table.insertRow(row)
                self.programs_table.setItem(row, 0, QTableWidgetItem(str(data[0])))
                self.programs_table.setItem(row, 1, QTableWidgetItem(data[1]))

    def load_clients(self):
        query = """SELECT DISTINCT c.client_id, CONCAT(c.first_name, ' ', c.last_name)
                   FROM clients c
                   WHERE c.client_id IN (SELECT client_id FROM personal_training_sessions WHERE trainer_id = %s)
                   OR c.client_id IN (SELECT ce.client_id FROM class_enrollments ce JOIN class_schedule cs ON ce.schedule_id = cs.schedule_id JOIN group_classes gc ON cs.class_id = gc.class_id WHERE gc.trainer_id = %s)
                """
        results = self.db.execute_query(query, (self.trainer_id, self.trainer_id))
        self.client_combo.clear()
        if results:
            for client_id, name in results:
                self.client_combo.addItem(name, client_id)

    def create_program(self):
        name = self.program_name_input.text()
        description = self.program_desc_input.toPlainText()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название программы.")
            return
        query = "INSERT INTO training_programs (trainer_id, name, description) VALUES (%s, %s, %s)"
        result = self.db.execute_insert(query, (self.trainer_id, name, description))
        if result:
            QMessageBox.information(self, "Успех", "Программа создана.")
            self.load_programs()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось создать программу.")

    def load_exercises_for_selected_program(self):
        selected_items = self.programs_table.selectedItems()
        if not selected_items:
            self.exercises_table.setRowCount(0)
            return
        program_id = self.programs_table.item(selected_items[0].row(), 0).text()
        query = "SELECT exercise_name, sets, reps, notes FROM program_exercises WHERE program_id = %s"
        results = self.db.execute_query(query, (program_id,))
        self.exercises_table.setRowCount(0)
        if results:
            for row, data in enumerate(results):
                self.exercises_table.insertRow(row)
                for col, item_data in enumerate(data):
                    self.exercises_table.setItem(row, col, QTableWidgetItem(str(item_data)))

    def open_add_exercise_dialog(self):
        selected_items = self.programs_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите программу.")
            return
        program_id = self.programs_table.item(selected_items[0].row(), 0).text()
        dlg = AddExerciseDialog(self.db, program_id, self.load_exercises_for_selected_program)
        dlg.exec()

    def assign_program(self):
        selected_program_items = self.programs_table.selectedItems()
        if not selected_program_items:
            QMessageBox.warning(self, "Ошибка", "Выберите программу для назначения.")
            return
        program_id = self.programs_table.item(selected_program_items[0].row(), 0).text()
        client_id = self.client_combo.currentData()
        if not client_id:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента.")
            return

        query = "INSERT INTO client_programs (client_id, program_id, assigned_date) VALUES (%s, %s, %s)"
        params = (client_id, program_id, QDate.currentDate().toString('yyyy-MM-dd'))
        try:
            result = self.db.execute_insert(query, params)
            if result:
                QMessageBox.information(self, "Успех", "Программа успешно назначена клиенту.")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось назначить программу. Возможно, она уже назначена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
