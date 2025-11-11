# Qt Designer and .ui files — Quick Guide

This short guide explains how to use Qt Designer to create graphical user interfaces (GUIs) and how to use the generated .ui files in Python (PySide6).

## 1) What is Qt Designer?

- Qt Designer is a visual editor to design Qt GUIs. It allows dragging widgets onto forms and saving layouts as `.ui` XML files.
- `.ui` files are XML descriptions of widgets, layouts and properties. They are not executable by themselves.

## 2) Two common ways to use a `.ui` file in Python

1. Load the `.ui` file at runtime (dynamic loading)

   - Use `PySide6.QtUiTools.loadUi` or `pyside6uic` depending on your environment.
   - Example (dynamic load):

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import loadUi
import sys

app = QApplication(sys.argv)
win = QMainWindow()
loadUi('myform.ui', win)  # populates `win` with widgets from .ui
win.show()
sys.exit(app.exec())
```

2. Convert the `.ui` to a Python module (static conversion)

   - Use the `pyside6-uic` tool to convert `.ui` into a `.py` file and import it.
   - Command:

```
pyside6-uic myform.ui -o ui_myform.py
```

   - Then in Python:

```python
from PySide6.QtWidgets import QMainWindow
from ui_myform import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

```

## 3) Which approach to choose?

- Dynamic loading is simple during development and keeps the designer file editable.
- Static conversion (uic) produces plain Python you can debug and extends better for production packaging.

## 4) Tips and gotchas

- Keep widget objectNames meaningful (you will reference these in code).
- Prefer layouts (QVBoxLayout, QHBoxLayout, QGridLayout) — they make resizing robust.
- Avoid complex custom widgets in Designer unless you know how to promote widgets (Promote to... option).
- If using QWebEngineView, remember to import and initialize WebEngine (PySide6-WebEngine package).
- When packaging (PyInstaller / cx_Freeze), include `.ui` or converted `.py` as needed.

## 5) Quick workflow suggestion

1. Build basic layout in Qt Designer and save `form.ui`.
2. If active development: load `.ui` dynamically.
3. For release: convert `.ui` to `.py` via `pyside6-uic` and import the generated module.

## 6) Example: Load .ui dynamically with PySide6

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import loadUi
import sys

app = QApplication(sys.argv)
window = QMainWindow()
loadUi('path/to/form.ui', window)
window.show()
sys.exit(app.exec())
```

## 7) References

- Qt Designer documentation: https://doc.qt.io/qt-6/qtdesigner-manual.html
- PySide6 docs: https://doc.qt.io/qtforpython/

---
This guide is intentionally short. If you want, I can create a small example `.ui` and the converted `.py`, or show how to promote custom widgets and load resources (.qrc).
