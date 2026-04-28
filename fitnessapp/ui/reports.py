from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QDateEdit, QHeaderView,
                             QComboBox, QMessageBox, QTabWidget)
from .chart_widget import ChartWidget
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta

class ReportsWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Отчеты и аналитика")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Report selection
        report_layout = QHBoxLayout()
        
        report_layout.addWidget(QLabel("Тип отчета:"))
        self.report_combo = QComboBox()
        self.report_combo.addItems([
            'Отчет о посещениях',
            'Отчет об абонементах',
            'Популярность занятий',
            'Производительность тренеров',
            'Отчет о доходах',
            'Активность клиентов'
        ])
        self.report_combo.currentTextChanged.connect(self.on_report_changed)
        report_layout.addWidget(self.report_combo)
        
        report_layout.addWidget(QLabel("От даты:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        report_layout.addWidget(self.from_date)
        
        report_layout.addWidget(QLabel("До даты:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        report_layout.addWidget(self.to_date)
        
        generate_btn = QPushButton("Создать отчет")
        generate_btn.clicked.connect(self.generate_report)
        report_layout.addWidget(generate_btn)
        
        layout.addLayout(report_layout)
        
        # Report table
        self.report_table = QTableWidget()
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.report_table)
        
        # Summary section
        layout.addWidget(QLabel("Сводка:"))
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(['Метрика', 'Значение'])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.summary_table.setMaximumHeight(200)
        layout.addWidget(self.summary_table)

        # Chart widget
        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)

        
        refresh_btn = QPushButton("Обновить отчет")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)
        self.refresh_data()

    def on_report_changed(self):
        self.generate_report()

    def refresh_data(self):
        self.load_report_data()

    def load_report_data(self):
        self.generate_report()

    def generate_report(self):
        report_type = self.report_combo.currentText()
        from_date = self.from_date.date().toString('yyyy-MM-dd')
        to_date = self.to_date.date().toString('yyyy-MM-dd')
        
        if report_type == 'Отчет о посещениях':
            self.attendance_report(from_date, to_date)
        elif report_type == 'Отчет об абонементах':
            self.membership_report(from_date, to_date)
        elif report_type == 'Популярность занятий':
            self.class_popularity_report(from_date, to_date)
        elif report_type == 'Производительность тренеров':
            self.trainer_performance_report(from_date, to_date)
        elif report_type == 'Отчет о доходах':
            self.revenue_report(from_date, to_date)
        elif report_type == 'Активность клиентов':
            self.client_activity_report(from_date, to_date)

    def attendance_report(self, from_date, to_date):
        query = """
        SELECT DATE(a.check_in_time) as date, COUNT(*) as total_visits
        FROM attendance a
        WHERE DATE(a.check_in_time) BETWEEN %s AND %s
        GROUP BY DATE(a.check_in_time)
        ORDER BY date ASC
        """
        results = self.db.execute_query(query, (from_date, to_date))

        self.report_table.setColumnCount(2)
        self.report_table.setHorizontalHeaderLabels(['Дата', 'Всего посещений'])
        self.report_table.setRowCount(0)

        total_visits = 0
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                # Format date for table
                date_val = row_data[0].strftime('%Y-%m-%d')
                visits_val = str(row_data[1])
                self.report_table.setItem(row_idx, 0, QTableWidgetItem(date_val))
                self.report_table.setItem(row_idx, 1, QTableWidgetItem(visits_val))
                total_visits += row_data[1]

        # Summary
        self.summary_table.setRowCount(0)
        summary_data = [
            ('Всего посещений за период', str(total_visits)),
            ('Среднее посещений в день', str(round(total_visits / len(results), 2) if results else 0))
        ]
        for row_idx, (metric, value) in enumerate(summary_data):
            self.summary_table.insertRow(row_idx)
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(value))

        # Plot data
        if results:
            dates = [row[0] for row in results]
            visits = [row[1] for row in results]
            x_ticks = list(range(len(dates)))
            
            # Convert date objects to timestamps for plotting
            x_data = [datetime.combine(d, datetime.min.time()).timestamp() for d in dates]

            self.chart_widget.plot_data(x_data, visits, title="Динамика посещений", x_label="Дата", y_label="Количество посещений")
            ax = self.chart_widget.plot_widget.getAxis('bottom')
            ticks = [list(zip(x_data, [d.strftime('%Y-%m-%d') for d in dates]))]
            ax.setTicks(ticks)

    def membership_report(self, from_date, to_date):
        query = """
        SELECT mt.name, COUNT(*) as sold, SUM(m.price_paid) as revenue,
               SUM(m.discount_applied) as total_discount
        FROM memberships m
        JOIN membership_types mt ON m.membership_type_id = mt.membership_type_id
        WHERE DATE(m.purchase_date) BETWEEN %s AND %s
        GROUP BY mt.name
        ORDER BY sold DESC
        """
        results = self.db.execute_query(query, (from_date, to_date))
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(['Тип абонемента', 'Продано', 'Доход', 'Всего скидок'])
        self.report_table.setRowCount(0)
        
        total_revenue = 0
        total_sold = 0
        
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "0")
                    self.report_table.setItem(row_idx, col_idx, item)
                
                total_sold += row_data[1]
                total_revenue += row_data[2] if row_data[2] else 0
        
        # Summary
        self.summary_table.setRowCount(0)
        summary_data = [
            ('Всего продано абонементов', str(total_sold)),
            ('Общий доход', f"{total_revenue:.2f} руб.")
        ]
        
        for row_idx, (metric, value) in enumerate(summary_data):
            self.summary_table.insertRow(row_idx)
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(value))

    def class_popularity_report(self, from_date, to_date):
        query = """
        SELECT gc.name, COUNT(ce.enrollment_id) as enrollments,
               gc.max_participants,
               ROUND(COUNT(ce.enrollment_id) * 100.0 / NULLIF(gc.max_participants, 0), 2) as occupancy_rate
        FROM group_classes gc
        LEFT JOIN class_schedule cs ON gc.class_id = cs.class_id
        LEFT JOIN class_enrollments ce ON cs.schedule_id = ce.schedule_id AND ce.class_date BETWEEN %s AND %s
        GROUP BY gc.class_id, gc.name, gc.max_participants
        ORDER BY enrollments DESC
        """
        results = self.db.execute_query(query, (from_date, to_date))
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(['Название занятия', 'Записей', 'Макс вместимость', 'Заполненность (%)'])
        self.report_table.setRowCount(0)
        
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "0")
                    self.report_table.setItem(row_idx, col_idx, item)
        
        # Summary
        self.summary_table.setRowCount(0)
        summary_data = [
            ('Всего занятий', str(len(results)) if results else '0'),
            ('Самое популярное занятие', results[0][0] if results else 'Н/Д')
        ]
        
        for row_idx, (metric, value) in enumerate(summary_data):
            self.summary_table.insertRow(row_idx)
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(value))

    def trainer_performance_report(self, from_date, to_date):
        query = """
        SELECT CONCAT(t.first_name, ' ', t.last_name) as trainer,
               COUNT(DISTINCT pts.session_id) as sessions,
               COUNT(DISTINCT ce.enrollment_id) as class_enrollments,
               COUNT(DISTINCT pts.client_id) as unique_clients
        FROM trainers t
        LEFT JOIN personal_training_sessions pts ON t.trainer_id = pts.trainer_id
               AND DATE(pts.session_date) BETWEEN %s AND %s
        LEFT JOIN group_classes gc ON t.trainer_id = gc.trainer_id
        LEFT JOIN class_schedule cs ON gc.class_id = cs.class_id
        LEFT JOIN class_enrollments ce ON cs.schedule_id = ce.schedule_id
               AND DATE(ce.class_date) BETWEEN %s AND %s
        WHERE t.status = 'active'
        GROUP BY t.trainer_id
        ORDER BY sessions DESC
        """
        results = self.db.execute_query(query, (from_date, to_date, from_date, to_date))
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(['Тренер', 'Персональные сеансы', 'Записи на занятия', 'Уникальные клиенты'])
        self.report_table.setRowCount(0)
        
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "0")
                    self.report_table.setItem(row_idx, col_idx, item)
        
        # Summary
        self.summary_table.setRowCount(0)
        summary_data = [
            ('Всего тренеров', str(len(results)) if results else '0'),
            ('Лучший тренер', results[0][0] if results else 'Н/Д')
        ]
        
        for row_idx, (metric, value) in enumerate(summary_data):
            self.summary_table.insertRow(row_idx)
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(value))

    def revenue_report(self, from_date, to_date):
        # Note: The purchase_date column might not exist in the original schema. Make sure it's added.
        query = """
        SELECT DATE(m.purchase_date) as date, COUNT(*) as memberships_sold,
               SUM(m.price_paid) as revenue, SUM(m.discount_applied) as discounts
        FROM memberships m
        WHERE m.purchase_date IS NOT NULL AND DATE(m.purchase_date) BETWEEN %s AND %s
        GROUP BY DATE(m.purchase_date)
        ORDER BY date DESC
        """
        results = self.db.execute_query(query, (from_date, to_date))
        
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(['Дата', 'Продано абонементов', 'Доход', 'Скидки'])
        self.report_table.setRowCount(0)
        
        total_revenue = 0
        total_discounts = 0
        
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    if col_idx > 1:
                        item = QTableWidgetItem(f"{value:.2f} руб." if value else "0.00 руб.")
                    else:
                        item = QTableWidgetItem(str(value) if value else "0")
                    self.report_table.setItem(row_idx, col_idx, item)
                
                total_revenue += row_data[2] if row_data[2] else 0
                total_discounts += row_data[3] if row_data[3] else 0
        
        # Summary
        self.summary_table.setRowCount(0)
        summary_data = [
            ('Общий доход', f"{total_revenue:.2f} руб."),
            ('Всего скидок', f"{total_discounts:.2f} руб."),
            ('Чистый доход', f"{total_revenue - total_discounts:.2f} руб.")
        ]
        
        for row_idx, (metric, value) in enumerate(summary_data):
            self.summary_table.insertRow(row_idx)
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(value))

    def client_activity_report(self, from_date, to_date):
        query = """
        SELECT c.client_id, CONCAT(c.first_name, ' ', c.last_name) as client_name,
               COUNT(DISTINCT a.attendance_id) as visits,
               COUNT(DISTINCT ce.enrollment_id) as classes_attended,
               COUNT(DISTINCT pts.session_id) as personal_sessions
        FROM clients c
        LEFT JOIN attendance a ON c.client_id = a.client_id
               AND DATE(a.check_in_time) BETWEEN %s AND %s
        LEFT JOIN class_enrollments ce ON c.client_id = ce.client_id
               AND DATE(ce.class_date) BETWEEN %s AND %s
               AND ce.attendance_status = 'attended'
        LEFT JOIN personal_training_sessions pts ON c.client_id = pts.client_id
               AND DATE(pts.session_date) BETWEEN %s AND %s
               AND pts.status = 'completed'
        WHERE c.status = 'active'
        GROUP BY c.client_id
        ORDER BY visits DESC
        LIMIT 50
        """
        results = self.db.execute_query(query, (from_date, to_date, from_date, to_date, from_date, to_date))
        
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(['ID клиента', 'Имя клиента', 'Посещения', 'Посещенные занятия', 'Персональные сеансы'])
        self.report_table.setRowCount(0)
        
        if results:
            for row_idx, row_data in enumerate(results):
                self.report_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value else "0")
                    self.report_table.setItem(row_idx, col_idx, item)
        
        # Summary
        self.summary_table.setRowCount(0)
        summary_data = [
            ('Активные клиенты', str(len(results)) if results else '0'),
            ('Самый активный клиент', results[0][1] if results else 'Н/Д')
        ]
        
        for row_idx, (metric, value) in enumerate(summary_data):
            self.summary_table.insertRow(row_idx)
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(value))
