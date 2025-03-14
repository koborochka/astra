import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QFormLayout, QHeaderView, QSplitter, QComboBox, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QIcon, QFont, QRegExpValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Устанавливаем шрифт "Courier New" размером 16px (12pt)
FONT = QFont("Courier New", 12)


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")
        self.setFont(FONT)
        self.layout = QFormLayout()

        # Название: максимум 12 символов, начинается с буквы, только буквы и цифры
        self.name_input = QLineEdit()
        name_validator = QRegExpValidator(QRegExp("^[А-Яа-яA-Za-z][А-Яа-яA-Za-z0-9]{0,11}$"))
        self.name_input.setValidator(name_validator)

        # Широта: от -90 до 90
        self.lat_input = QLineEdit()
        lat_validator = QRegExpValidator(QRegExp("^-?(90|[0-8]?\\d)(\\.\\d+)?$"))
        self.lat_input.setValidator(lat_validator)

        # Долгота: от -180 до 180
        self.lon_input = QLineEdit()
        lon_validator = QRegExpValidator(QRegExp("^-?(180|1[0-7]\\d|\\d{1,2})(\\.\\d+)?$"))
        self.lon_input.setValidator(lon_validator)

        # Тип: выпадающий список
        self.type_input = QComboBox()
        self.type_input.addItems(["Пункт", "Госпиталь", "Место"])

        # Количество: от 1 до 100 для мест, от 10 до 100 для пунктов
        self.amount_input = QLineEdit()
        amount_validator = QRegExpValidator(QRegExp("^([1-9]\\d?|100)$"))
        self.amount_input.setValidator(amount_validator)

        self.layout.addRow("Название:", self.name_input)
        self.layout.addRow("Широта:", self.lat_input)
        self.layout.addRow("Долгота:", self.lon_input)
        self.layout.addRow("Тип:", self.type_input)
        self.layout.addRow("Количество:", self.amount_input)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.accept)
        self.add_button.setFont(FONT)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def get_values(self):
        return (
            self.name_input.text(), self.lat_input.text(),
            self.lon_input.text(), self.type_input.currentText(), self.amount_input.text()
        )


class TableApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Table App")
        self.setWindowIcon(QIcon('icon.png'))
        self.setGeometry(100, 100, 1200, 600)
        self.setFont(FONT)

        # Основной макет
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # Левая часть: таблица и кнопки (40%)
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_widget.setLayout(self.left_layout)

        # Таблица
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Широта", "Долгота", "Тип", "Количество"])
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: gray; }")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Растягиваем столбцы
        self.table.setFont(FONT)
        self.left_layout.addWidget(self.table)

        # Кнопки
        self.button_layout = QVBoxLayout()
        self.button_row1 = QHBoxLayout()
        self.button_row2 = QHBoxLayout()

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.open_add_dialog)
        self.add_button.setStyleSheet("QPushButton { background-color: green; }")
        self.add_button.setFont(FONT)
        self.button_row1.addWidget(self.add_button)

        self.import_button = QPushButton("Импорт")
        self.import_button.setFont(FONT)
        self.button_row1.addWidget(self.import_button)

        self.report_button = QPushButton("Отчет")
        self.report_button.clicked.connect(self.toggle_plot)
        self.report_button.setFont(FONT)
        self.button_row1.addWidget(self.report_button)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_table)
        self.clear_button.setFont(FONT)
        self.button_row2.addWidget(self.clear_button)

        self.link_button = QPushButton("Связывание")
        self.link_button.setFont(FONT)
        self.button_row2.addWidget(self.link_button)

        self.place_button = QPushButton("Размещение")
        self.place_button.setFont(FONT)
        self.button_row2.addWidget(self.place_button)

        self.button_layout.addLayout(self.button_row1)
        self.button_layout.addLayout(self.button_row2)
        self.left_layout.addLayout(self.button_layout)

        # Правая часть: пустой квадрат или график (60%)
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_widget.setLayout(self.right_layout)

        # Пустой квадрат
        self.empty_frame = QFrame()
        self.empty_frame.setStyleSheet("background-color: white; border: 1px solid black;")
        self.right_layout.addWidget(self.empty_frame)

        # График
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.right_layout.addWidget(self.canvas)
        self.canvas.hide()  # Скрываем график по умолчанию

        # Разделитель (40% - левая часть, 60% - правая часть)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([400, 600])  # 40% и 60%
        self.main_layout.addWidget(self.splitter)

        # Инициализация данных
        self.row_id = 1
        self.add_mock_data()

    def add_mock_data(self):
        mock_data = [
            ("Парк", "55.751244", "37.618423", "Место", "10"),
            ("Кафе", "55.752023", "37.615310", "Пункт", "50")
        ]
        for name, lat, lon, type_, amount in mock_data:
            self.add_row(name, lat, lon, type_, amount)

    def open_add_dialog(self):
        dialog = AddDialog(self)
        if dialog.exec_():
            name, lat, lon, type_, amount = dialog.get_values()
            if self.validate_input(name, lat, lon, type_, amount):
                self.add_row(name, lat, lon, type_, amount)

    def validate_input(self, name, lat, lon, type_, amount):
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            amount_int = int(amount)

            if not (-90 <= lat_float <= 90):
                raise ValueError("Широта должна быть в диапазоне от -90 до 90.")
            if not (-180 <= lon_float <= 180):
                raise ValueError("Долгота должна быть в диапазоне от -180 до 180.")
            if type_ == "Место" and not (1 <= amount_int <= 100):
                raise ValueError("Количество раненых должно быть от 1 до 100.")
            if type_ == "Пункт" and not (10 <= amount_int <= 100):
                raise ValueError("Вместимость пункта должна быть от 10 до 100.")
            if type_ == "Госпиталь" and not (1 <= amount_int <= 10):
                raise ValueError("Количество госпиталей должно быть от 1 до 10.")

            return True
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return False

    def add_row(self, name="", lat="0.0", lon="0.0", type_="Пункт", amount="0"):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(str(self.row_id)))
        self.table.item(row_position, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row_position, 1, QTableWidgetItem(name))
        self.table.setItem(row_position, 2, QTableWidgetItem(lat))
        self.table.item(row_position, 2).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row_position, 3, QTableWidgetItem(lon))
        self.table.item(row_position, 3).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.table.setItem(row_position, 4, QTableWidgetItem(type_))
        self.table.setItem(row_position, 5, QTableWidgetItem(amount))
        self.row_id += 1

    def clear_table(self):
        self.table.setRowCount(0)
        self.row_id = 1

    def toggle_plot(self):
        if self.canvas.isVisible():
            self.canvas.hide()
            self.empty_frame.show()
            self.report_button.setStyleSheet("")  # Убираем подсветку кнопки "Отчет"
            self.add_button.setStyleSheet("QPushButton { background-color: white; }")  # Кнопка "Добавить" белая
        else:
            self.update_plot()
            self.canvas.show()
            self.empty_frame.hide()
            self.report_button.setStyleSheet("QPushButton { background-color: green; }")  # Подсвечиваем кнопку "Отчет"
            self.add_button.setStyleSheet("QPushButton { background-color: green; }")  # Кнопка "Добавить" зеленая

    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        lats = [float(self.table.item(i, 2).text()) for i in range(self.table.rowCount())]
        lons = [float(self.table.item(i, 3).text()) for i in range(self.table.rowCount())]
        ax.scatter(lons, lats)
        ax.set_xlabel("Долгота")
        ax.set_ylabel("Широта")
        ax.set_title("График широта-долгота")
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TableApp()
    window.show()
    sys.exit(app.exec_())
