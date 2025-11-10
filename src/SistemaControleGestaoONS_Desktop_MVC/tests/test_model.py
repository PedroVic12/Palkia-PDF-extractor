import unittest
import os
import sys

# Add the project root to the Python path to allow imports from the app
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from pomodoro_todo_app.model import TodoModel

class TestTodoModel(unittest.TestCase):

    def setUp(self):
        """
        Configura um banco de dados em memória para cada teste.
        Isso garante que os testes sejam independentes e não deixem lixo no disco.
        """
        self.db_path = "file::memory:?cache=shared"
        self.model = TodoModel(db_path=self.db_path)

    def test_add_task(self):
        """Testa se uma tarefa pode ser adicionada."""
        self.model.add_task("Test Task 1")
        tasks = self.model.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['descricao'], "Test Task 1")
        self.assertEqual(tasks[0]['concluida'], 0)

    def test_update_task_status(self):
        """Testa se o status de uma tarefa pode ser atualizado."""
        self.model.add_task("Test Task 2")
        task_id = self.model.get_tasks()[0]['id']
        
        # Marca como concluída
        self.model.update_task_status(task_id, True)
        task = self.model.get_tasks()[0]
        self.assertEqual(task['concluida'], 1)
        
        # Marca como pendente novamente
        self.model.update_task_status(task_id, False)
        task = self.model.get_tasks()[0]
        self.assertEqual(task['concluida'], 0)

    def test_delete_task(self):
        """Testa se uma tarefa pode ser deletada."""
        self.model.add_task("Task to be deleted")
        tasks_before = self.model.get_tasks()
        self.assertEqual(len(tasks_before), 1)
        
        task_id = tasks_before[0]['id']
        self.model.delete_task(task_id)
        
        tasks_after = self.model.get_tasks()
        self.assertEqual(len(tasks_after), 0)

    def test_increment_pomodoro_cycle(self):
        """Testa se o contador de ciclos pomodoro é incrementado."""
        self.model.add_task("Pomodoro Task")
        task_id = self.model.get_tasks()[0]['id']
        
        # Verifica o valor inicial
        task_before = self.model.get_tasks()[0]
        self.assertEqual(task_before['ciclos_pomodoro'], 0)
        
        # Incrementa o ciclo
        self.model.increment_pomodoro_cycle(task_id)
        
        # Verifica o novo valor
        task_after = self.model.get_tasks()[0]
        self.assertEqual(task_after['ciclos_pomodoro'], 1)

    def test_get_tasks_order(self):
        """Testa se as tarefas são retornadas em ordem decrescente de criação."""
        self.model.add_task("First Task")
        self.model.add_task("Second Task")
        
        tasks = self.model.get_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['descricao'], "Second Task")
        self.assertEqual(tasks[1]['descricao'], "First Task")

if __name__ == '__main__':
    unittest.main()
