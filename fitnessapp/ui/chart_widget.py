import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

    def plot_data(self, x_data, y_data, title="", x_label="", y_label=""):
        self.plot_widget.clear()
        self.plot_widget.plot(x_data, y_data, pen='b', symbol='o', symbolBrush='r')
        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel('left', y_label)
        self.plot_widget.setLabel('bottom', x_label)
