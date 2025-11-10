from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QLineEdit, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont

# We need to adjust the import path to find the model
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from model import TodoModel

class ChecklistWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Each checklist has its own model instance
        self.model = TodoModel()
        
        self.main_layout = QVBoxLayout(self)
        
        self._create_input_widgets()
        self._create_list_widget()
        self._create_action_buttons()
        
        # Connect model signal to the view's slot
        self.model.tasks_changed.connect(self.render_tasks)
        
        # Initial render
        self.render_tasks()

    def _create_input_widgets(self):
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Adicionar nova tarefa e pressionar Enter...")
        self.task_input.returnPressed.connect(self.add_task)
        
        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self.add_task)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_button)
        self.main_layout.addLayout(input_layout)

    def _create_list_widget(self):
        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.toggle_task_status)
        self.main_layout.addWidget(self.task_list)

    def _create_action_buttons(self):
        self.delete_button = QPushButton("Remover Tarefas Concluídas")
        self.delete_button.clicked.connect(self.delete_completed)
        self.main_layout.addWidget(self.delete_button)

    @Slot()
    def add_task(self):
        description = self.task_input.text().strip()
        if description:
            self.model.add_task(description)
            self.task_input.clear()

    @Slot(QListWidgetItem)
    def toggle_task_status(self, item):
        task_id = item.data(Qt.UserRole)
        is_completed = item.checkState() == Qt.Checked
        # Block signals to prevent render_tasks from re-triggering this
        self.task_list.blockSignals(True)
        self.model.update_task_status(task_id, is_completed)
        self.task_list.blockSignals(False)

    @Slot()
    def delete_completed(self):
        self.model.delete_completed_tasks()

    @Slot()
    def render_tasks(self):
        # Block signals to prevent itemChanged from firing during refresh
        self.task_list.blockSignals(True)
        self.task_list.clear()
        tasks = self.model.get_tasks()
        
        for task in tasks:
            item = QListWidgetItem(task['descricao'])
            item.setData(Qt.UserRole, task['id'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            if task['concluida']:
                item.setCheckState(Qt.Checked)
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
                item.setForeground(Qt.gray)
            else:
                item.setCheckState(Qt.Unchecked)
            
            self.task_list.addItem(item)
            
        self.task_list.blockSignals(False)

    def closeEvent(self, event):
        """Ensure the database connection is closed when the widget is destroyed."""
        self.model.close()
        super().closeEvent(event)
