"""
tree_mvc_app.py

Single-file MVC example application using PySide6.

Features:
- Dark / Light theme toggle (styles taken from `app_desktop.py` in this repo).
- Left side tree menu (like `Qt6_desktop_template.py`).
- Central QTabWidget hosting "iframes" (QWebEngineView when available, QTextBrowser fallback).
- Controller allows creating new iframe tabs, closing tabs and opening items from the tree.

How to run:
  python tree_mvc_app.py

Requirements: PySide6. For real web iframes, install PySide6-WebEngine (optional).
This file implements a minimal MVC separation: Model, View, Controller classes.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QTabWidget, QToolBar,
    QTextBrowser, QInputDialog, QMessageBox, QLineEdit, QLabel
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QAction
try:
    from PySide6.QtUiTools import loadUi
except Exception:
    # fallback if QtUiTools not available
    loadUi = None

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEB_AVAILABLE = True
except Exception:
    QWebEngineView = None  # type: ignore
    WEB_AVAILABLE = False


# ------------------ Styles (dark / light) ------------------
DARK_STYLE = """
    QWidget { background-color: #202020; color: #FFFFFF; font-family: 'Segoe UI'; }
    #Sidebar { background-color: #2D2D2D; border-right: 1px solid #404040; }
    #ContentFrame { background-color: #202020; }
    QPushButton { background-color: #3C3C3C; color: #fff; }
"""

LIGHT_STYLE = """
    QWidget { background-color: #F3F3F3; color: #000000; font-family: 'Segoe UI'; }
    #Sidebar { background-color: #E0E0E0; border-right: 1px solid #C0C0C0; }
    #ContentFrame { background-color: #F3F3F3; }
    QPushButton { background-color: #FFFFFF; color: #000; }
"""


# ------------------ Model ------------------
class PagesModel(QObject):
    """Simple model holding information about opened pages/tabs."""

    pages_changed = Signal()

    def __init__(self):
        super().__init__()
        self._pages: List[dict] = []

    def add_page(self, title: str, url: Optional[str] = None, use_web: bool = True):
        self._pages.append({"title": title, "url": url, "use_web": use_web})
        self.pages_changed.emit()

    def remove_page(self, index: int):
        if 0 <= index < len(self._pages):
            del self._pages[index]
            self.pages_changed.emit()

    def get_pages(self) -> List[dict]:
        return list(self._pages)


# ------------------ View ------------------
class MainWindow(QMainWindow):
    create_page_requested = Signal(str, str)  # title, url
    close_page_requested = Signal(int)
    open_tree_item_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree MVC - Tabs / Iframes")
        self.resize(1000, 700)
        self._dark = True

        # Attempt to load UI from .ui file created with Qt Designer. If not found,
        # fall back to programmatic construction.
        ui_path = Path(__file__).resolve().parent / "tree_mvc_main.ui"
        if loadUi and ui_path.exists():
            try:
                loadUi(str(ui_path), self)
                # map designer object names to expected attributes used below
                # designer widget names: treeWidget, addIframeBtn, toggleThemeBtn, tabWidget, statusLabel
                self.tree = getattr(self, 'treeWidget', None)
                self.add_iframe_btn = getattr(self, 'addIframeBtn', None)
                self.toggle_theme_btn = getattr(self, 'toggleThemeBtn', None)
                self.tabs = getattr(self, 'tabWidget', None)
                self.status_label = getattr(self, 'statusLabel', None)
            except Exception:
                # if load fails, build fallback UI
                self._build_fallback_ui()
        else:
            self._build_fallback_ui()

        # Populate the tree with sample nodes (if tree exists)
        if getattr(self, 'tree', None):
            self._populate_tree()

        # Connections (guard if widgets missing)
        if getattr(self, 'add_iframe_btn', None):
            self.add_iframe_btn.clicked.connect(self._on_create_iframe_clicked)
        if getattr(self, 'toggle_theme_btn', None):
            self.toggle_theme_btn.clicked.connect(self._on_toggle_theme)
        if getattr(self, 'tree', None):
            self.tree.itemDoubleClicked.connect(self._on_tree_item_double_clicked)
        if getattr(self, 'tabs', None):
            self.tabs.tabCloseRequested.connect(self._on_tab_close_requested)

        # Apply default theme
        self.apply_theme("dark")

    def _build_fallback_ui(self):
        # programmatic fallback UI (kept from previous implementation)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Sidebar (tree)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(6, 6, 6, 6)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        sidebar_layout.addWidget(self.tree)

        # Quick controls above the tree
        self.add_iframe_btn = QPushButton("+ Criar Iframe")
        sidebar_layout.addWidget(self.add_iframe_btn)

        self.toggle_theme_btn = QPushButton("Alternar Tema")
        sidebar_layout.addWidget(self.toggle_theme_btn)

        main_layout.addWidget(self.sidebar, 0)

        # Content: Tabs
        right = QWidget()
        right.setObjectName("ContentFrame")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(6, 6, 6, 6)

        toolbar = QToolBar()
        right_layout.addWidget(toolbar)

        self.status_label = QLabel("")
        toolbar.addWidget(self.status_label)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        right_layout.addWidget(self.tabs, 1)

        main_layout.addWidget(right, 1)

    def apply_theme(self, which: str):
        if which == "dark":
            self.setStyleSheet(DARK_STYLE)
            self._dark = True
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self._dark = False

    def _populate_tree(self):
        root = QTreeWidgetItem(["Lousa"])
        adicionar = QTreeWidgetItem(["Adicionar fotos e arquivos"])
        criar = QTreeWidgetItem(["Criar imagem"])
        pensar = QTreeWidgetItem(["Pensando"])
        investigar = QTreeWidgetItem(["Investigar"])
        estudar = QTreeWidgetItem(["Estudar e aprender"])
        mais = QTreeWidgetItem(["Mais"])

        root.addChildren([adicionar, criar, pensar, investigar, estudar, mais])

        busca_web = QTreeWidgetItem(["Busca na Web"])
        mais.addChild(busca_web)

        self.tree.addTopLevelItem(root)
        self.tree.expandAll()

    # UI helpers
    def add_tab_with_widget(self, widget, title: str):
        self.tabs.addTab(widget, title)
        self.tabs.setCurrentWidget(widget)
        self.status_label.setText(f"Abriu: {title}")

    # event handlers
    def _on_create_iframe_clicked(self):
        title, ok = QInputDialog.getText(self, "Criar Iframe", "Título:")
        if not ok or not title.strip():
            return
        url, ok2 = QInputDialog.getText(self, "Criar Iframe", "URL (opcional):")
        if not ok2:
            url = ""
        self.create_page_requested.emit(title.strip(), url.strip())

    def _on_toggle_theme(self):
        self.apply_theme("light" if self._dark else "dark")

    def _on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        self.open_tree_item_requested.emit(item.text(0))

    def _on_tab_close_requested(self, index: int):
        self.close_page_requested.emit(index)


# ------------------ Controller ------------------
class AppController:
    def __init__(self, model: PagesModel, view: MainWindow):
        self.model = model
        self.view = view

        # wire events
        self.view.create_page_requested.connect(self.handle_create_page)
        self.view.open_tree_item_requested.connect(self.handle_open_tree_item)
        self.view.close_page_requested.connect(self.handle_close_page)
        self.model.pages_changed.connect(self.sync_view_with_model)

    def handle_create_page(self, title: str, url: str):
        use_web = bool(url) and WEB_AVAILABLE
        # push to model
        self.model.add_page(title, url if url else None, use_web)

    def handle_open_tree_item(self, name: str):
        # If an existing tab with same title exists, focus it; otherwise create a simple page
        for idx, p in enumerate(self.model.get_pages()):
            if p["title"] == name:
                self.view.tabs.setCurrentIndex(idx)
                return
        # create a new page with the item name
        self.model.add_page(name, None, False)

    def handle_close_page(self, index: int):
        self.model.remove_page(index)

    def sync_view_with_model(self):
        # naive full sync: clear tabs and recreate from model list
        current_index = self.view.tabs.currentIndex()
        self.view.tabs.clear()
        for p in self.model.get_pages():
            title = p.get("title") or "Untitled"
            url = p.get("url")
            use_web = p.get("use_web", False)
            if use_web and WEB_AVAILABLE:
                w = QWebEngineView()
                if url:
                    w.load(url)
                else:
                    # blank page
                    w.setHtml(f"<h2>{title}</h2><p>Nova página (web)</p>")
            else:
                w = QTextBrowser()
                if url:
                    w.setSource(url)
                else:
                    w.setHtml(f"<h2>{title}</h2><p>Conteúdo interno.</p>")
            self.view.add_tab_with_widget(w, title)
        # restore sensible index
        if self.view.tabs.count() > 0:
            self.view.tabs.setCurrentIndex(min(current_index, self.view.tabs.count() - 1))


def main():
    app = QApplication(sys.argv)
    model = PagesModel()
    view = MainWindow()
    controller = AppController(model, view)
    view.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
