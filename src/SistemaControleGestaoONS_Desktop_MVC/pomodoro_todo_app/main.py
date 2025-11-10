import sys
from PySide6.QtWidgets import QApplication
from .model import TodoModel
from .view import PomodoroView
from .controller import PomodoroController

def main():
    app = QApplication(sys.argv)
    
    model = TodoModel()
    view = PomodoroView()
    controller = PomodoroController(model, view)
    
    view.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
