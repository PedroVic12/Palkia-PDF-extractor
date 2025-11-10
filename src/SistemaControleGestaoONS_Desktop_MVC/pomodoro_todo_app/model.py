import sqlite3
from PySide6.QtCore import QObject, Signal

class TodoModel(QObject):
    tasks_changed = Signal()

    def __init__(self, db_path='pomodoro_tasks.db'):
        super().__init__()
        self.db_path = db_path
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    concluida INTEGER NOT NULL DEFAULT 0,
                    ciclos_pomodoro INTEGER NOT NULL DEFAULT 0,
                    data_criacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get_tasks(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tarefas ORDER BY data_criacao DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_task(self, description):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tarefas (descricao) VALUES (?)", (description,))
            conn.commit()
        self.tasks_changed.emit()

    def update_task_status(self, task_id, completed):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET concluida = ? WHERE id = ?", (1 if completed else 0, task_id))
            conn.commit()
        self.tasks_changed.emit()

    def delete_task(self, task_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarefas WHERE id = ?", (task_id,))
            conn.commit()
        self.tasks_changed.emit()

    def increment_pomodoro_cycle(self, task_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tarefas SET ciclos_pomodoro = ciclos_pomodoro + 1 WHERE id = ?", (task_id,))
            conn.commit()
        self.tasks_changed.emit()
