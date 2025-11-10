from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QLabel, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class PomodoroView(QMainWindow):
    add_task_requested = Signal(str)
    delete_task_requested = Signal(int)
    toggle_task_status_requested = Signal(int, bool)
    start_pomodoro_requested = Signal()
    start_short_break_requested = Signal()
    start_long_break_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Todo-List")
        self.setGeometry(100, 100, 500, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_timer_widgets()
        self._create_task_widgets()
        self._apply_styles()

    def _create_timer_widgets(self):
        timer_layout = QVBoxLayout()
        
        self.timer_label = QLabel("25:00")
        self.timer_label.setFont(QFont("Arial", 60, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_label)

        buttons_layout = QHBoxLayout()
        self.pomodoro_button = QPushButton("Pomodoro (25 min)")
        self.short_break_button = QPushButton("Pausa Curta (5 min)")
        self.long_break_button = QPushButton("Pausa Longa (15 min)")
        
        buttons_layout.addWidget(self.pomodoro_button)
        buttons_layout.addWidget(self.short_break_button)
        buttons_layout.addWidget(self.long_break_button)
        timer_layout.addLayout(buttons_layout)

        self.main_layout.addLayout(timer_layout)

    def _create_task_widgets(self):
        task_layout = QVBoxLayout()

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Adicionar nova tarefa...")
        self.task_input.returnPressed.connect(self._on_add_task)
        task_layout.addWidget(self.task_input)

        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self._on_task_item_changed)
        task_layout.addWidget(self.task_list)
        
        self.delete_button = QPushButton("Remover Tarefa Concluída")
        task_layout.addWidget(self.delete_button)

        self.main_layout.addLayout(task_layout)

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLabel {
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #555;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4f5355;
            }
            QLineEdit {
                background-color: #333;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 5px;
            }
            QListWidget {
                background-color: #333;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)

    def _on_add_task(self):
        description = self.task_input.text()
        if description:
            self.add_task_requested.emit(description)
            self.task_input.clear()

    def _on_task_item_changed(self, item):
        task_id = item.data(Qt.UserRole)
        is_completed = item.checkState() == Qt.Checked
        self.toggle_task_status_requested.emit(task_id, is_completed)

    def render_tasks(self, tasks):
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for task in tasks:
            item = QListWidgetItem(task['descricao'])
            item.setData(Qt.UserRole, task['id'])
            item.setCheckState(Qt.Checked if task['concluida'] else Qt.Unchecked)
            font = item.font()
            font.setStrikeOut(task['concluida'])
            item.setFont(font)
            self.task_list.addItem(item)
        self.task_list.blockSignals(False)

    def update_timer_display(self, time_str):
        self.timer_label.setText(time_str)
