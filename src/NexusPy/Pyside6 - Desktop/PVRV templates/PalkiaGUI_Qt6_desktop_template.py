"""
Qt6_desktop_template.py

Merged single-file application combining features from:
- `app_desktop.py` (theme, Switch control, settings model)
- `dashboard_sp_desktop.py` (ActivityModel, Flask API, dashboard tabs)

The file provides a single MVC-style PySide6 desktop app that runs a Flask backend in a background thread
and a PySide6 front-end with a tree-style sidebar, tabs with iframes (QWebEngineView when available),
dark/light themes, and controls to load Excel and show dashboard/kanban/table.

How to run:
  python Qt6_desktop_template.py

Requirements:
  - Python packages: PySide6, Flask, pandas, requests
  - Optional: PySide6-WebEngine for real web iframes

"""

from __future__ import annotations
import sys
import os
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QSplitter, QTabWidget, QTextEdit, QListWidget,
    QMessageBox, QHeaderView, QFrame, QGridLayout, QScrollArea,
    QTreeWidget, QTreeWidgetItem, QToolBar, QInputDialog, QTextBrowser
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QIcon, QFont, QAction

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEB_AVAILABLE = True
except Exception:
    QWebEngineView = None  # type: ignore
    WEB_AVAILABLE = False


# ------------------ Styles (from app_desktop.py) ------------------
DARK_STYLE = """
    QWidget { background-color: #202020; color: #FFFFFF; font-family: 'Segoe UI'; font-size: 14px; }
    QMainWindow { background-color: #2D2D2D; }
    #Sidebar { background-color: #2D2D2D; border-right: 1px solid #404040; }
    #ContentFrame, #HeaderLabel { background-color: #202020; }
    QListWidget { border: none; padding-top: 10px; }
    QListWidget::item { padding: 12px 20px; border-radius: 5px; }
    QListWidget::item:hover { background-color: #353535; }
    QListWidget::item:selected { background-color: #0078D4; color: #FFFFFF; }
"""

LIGHT_STYLE = """
    QWidget { background-color: #F3F3F3; color: #000000; font-family: 'Segoe UI'; font-size: 14px; }
    QMainWindow { background-color: #E0E0E0; }
    #Sidebar { background-color: #E0E0E0; border-right: 1px solid #C0C0C0; }
    #ContentFrame, #HeaderLabel { background-color: #F3F3F3; }
"""


# ------------------ Small Switch widget (from app_desktop.py) ------------------
from PySide6.QtWidgets import QAbstractButton, QSizePolicy
from PySide6.QtCore import Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor

class Switch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)

        self._thumb_position = 0
        self.animation = QPropertyAnimation(self, b"thumb_position", self)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

        self.toggled.connect(self._handle_toggle)

    @Property(float)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        is_dark_mode = self.palette().window().color().lightness() < 128
        track_color = QColor("#0078D4") if self.isChecked() else QColor("#8E8E8E" if is_dark_mode else "#C0C0C0")
        thumb_color = QColor("#FFFFFF")
        track_radius = self.height() / 2

        painter.setBrush(track_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), track_radius, track_radius)

        thumb_y = 2
        thumb_size = self.height() - 4
        thumb_x = self._thumb_position * (self.width() - thumb_size - 4) + 2

        painter.setBrush(thumb_color)
        painter.drawEllipse(int(thumb_x), thumb_y, thumb_size, thumb_size)

    def _handle_toggle(self, checked):
        self.animation.setStartValue(self.thumb_position)
        self.animation.setEndValue(1.0 if checked else 0.0)
        self.animation.start()


# ------------------ Settings Model (small persistent store) ------------------
DB_FILE = "settings.db"

class SettingsModel(QObject):
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._theme = "dark"
        self._db_conn = self._create_db_connection()
        self._load_from_db()

    def _create_db_connection(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()
            return conn
        except sqlite3.Error:
            return None

    def _load_from_db(self):
        if not self._db_conn:
            return
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            settings = dict(cursor.fetchall())
            self._theme = settings.get("theme", self._theme)
        except Exception:
            pass

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, value):
        self._theme = value
        if self._db_conn:
            try:
                cursor = self._db_conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("theme", value))
                self._db_conn.commit()
            except Exception:
                pass
        self.theme_changed.emit(value)


# ------------------ ActivityModel + Flask API (from dashboard_sp_desktop.py) ------------------
class ActivityModel:
    def __init__(self):
        self.data: pd.DataFrame = pd.DataFrame()
        self.filtered_data: pd.DataFrame = pd.DataFrame()
        self.sheets: Dict[str, pd.DataFrame] = {}
        self.current_sheet = "Consolidado"
        self.filters = {'responsavel': 'Todos', 'status': 'Todos', 'ressalva': 'Todas'}

    def load_excel(self, filepath: str) -> bool:
        try:
            xls = pd.ExcelFile(filepath)
            self.sheets = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}
            all_data = []
            for sheet_name, df in self.sheets.items():
                df['ORIGEM'] = sheet_name
                all_data.append(df)
            self.data = pd.concat(all_data, ignore_index=True)
            self.filtered_data = self.data.copy()
            return True
        except Exception:
            return False

    def apply_filters(self):
        df = self.data.copy()
        if self.current_sheet != "Consolidado":
            df = df[df['ORIGEM'] == self.current_sheet]
        if self.filters['responsavel'] != 'Todos':
            df = df[df['RESPONSÁVEL'] == self.filters['responsavel']]
        if self.filters['status'] != 'Todos':
            df = df[df['STATUS'] == self.filters['status']]
        if self.filters['ressalva'] == 'Com Ressalvas':
            df = df[df['OBSERVAÇÃO'].notna() & (df['OBSERVAÇÃO'] != '')]
        elif self.filters['ressalva'] == 'Sem Ressalvas':
            df = df[df['OBSERVAÇÃO'].isna() | (df['OBSERVAÇÃO'] == '')]
        self.filtered_data = df

    def get_statistics(self) -> Dict:
        if self.filtered_data.empty:
            return {}
        return {
            'total': len(self.filtered_data),
            'pendentes': len(self.filtered_data[self.filtered_data['STATUS'] == 'Pendente']),
            'concluidos': len(self.filtered_data[self.filtered_data['STATUS'] == 'Concluído']),
            'responsaveis': self.filtered_data['RESPONSÁVEL'].nunique(),
            'com_ressalvas': len(self.filtered_data[self.filtered_data['OBSERVAÇÃO'].notna() & (self.filtered_data['OBSERVAÇÃO'] != '')])
        }

    def get_chart_data(self) -> Dict:
        if self.filtered_data.empty:
            return {}
        return {
            'status': self.filtered_data['STATUS'].value_counts().to_dict(),
            'responsaveis': self.filtered_data['RESPONSÁVEL'].value_counts().to_dict(),
            'ressalvas': {
                'Com Ressalvas': len(self.filtered_data[self.filtered_data['OBSERVAÇÃO'].notna() & (self.filtered_data['OBSERVAÇÃO'] != '')]),
                'Sem Ressalvas': len(self.filtered_data[self.filtered_data['OBSERVAÇÃO'].isna() | (self.filtered_data['OBSERVAÇÃO'] == '')])
            }
        }


# Flask backend
flask_app = Flask(__name__)
CORS(flask_app)
backend_model = ActivityModel()


@flask_app.route('/api/load', methods=['POST'])
def api_load():
    data = request.json
    filepath = data.get('filepath')
    if backend_model.load_excel(filepath):
        return jsonify({'success': True, 'sheets': list(backend_model.sheets.keys())})
    return jsonify({'success': False}), 400


@flask_app.route('/api/filter', methods=['POST'])
def api_filter():
    data = request.json
    if 'sheet' in data:
        backend_model.current_sheet = data['sheet']
    if 'responsavel' in data:
        backend_model.filters['responsavel'] = data['responsavel']
    if 'status' in data:
        backend_model.filters['status'] = data['status']
    if 'ressalva' in data:
        backend_model.filters['ressalva'] = data['ressalva']
    backend_model.apply_filters()
    return jsonify({'success': True})


@flask_app.route('/api/data', methods=['GET'])
def api_data():
    if backend_model.filtered_data.empty:
        return jsonify({'data': []})
    return jsonify({'data': backend_model.filtered_data.fillna('').to_dict(orient='records')})


@flask_app.route('/api/statistics', methods=['GET'])
def api_statistics():
    return jsonify(backend_model.get_statistics())


@flask_app.route('/api/charts', methods=['GET'])
def api_charts():
    return jsonify(backend_model.get_chart_data())


@flask_app.route('/api/export', methods=['GET'])
def api_export():
    if backend_model.filtered_data.empty:
        return jsonify({'error': 'Nenhum dado para exportar'}), 400
    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join('exports', filename)
    os.makedirs('exports', exist_ok=True)
    backend_model.filtered_data.to_excel(filepath, index=False)
    return jsonify({'success': True, 'filepath': filepath})


# Flask thread
class FlaskThread(QThread):
    def run(self):
        flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


# ------------------ MainWindow (merged UI) ------------------
class MainWindow(QMainWindow):
    def __init__(self, settings: SettingsModel):
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Palkia - Dashboard (Merged Template)")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)

        # Left: sidebar (tree + controls)
        sidebar = QFrame()
        sidebar.setObjectName('Sidebar')
        sidebar.setMaximumWidth(320)
        sb_layout = QVBoxLayout(sidebar)

        title = QLabel("Controles")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        sb_layout.addWidget(title)

        self.btn_load = QPushButton("📁 Carregar Excel")
        self.btn_load.clicked.connect(self.load_file)
        self.btn_export = QPushButton("💾 Exportar Dados")
        self.btn_export.clicked.connect(self.export_data)
        sb_layout.addWidget(self.btn_load)
        sb_layout.addWidget(self.btn_export)

        sb_layout.addWidget(QLabel("─" * 40))

        # Tree menu
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        root = QTreeWidgetItem(["Lousa"])
        nodes = ["Adicionar fotos e arquivos", "Criar imagem", "Pensando", "Investigar", "Estudar e aprender", "Mais"]
        children = [QTreeWidgetItem([n]) for n in nodes]
        root.addChildren(children)
        more = QTreeWidgetItem(["Busca na Web"])
        children[-1].addChild(more)
        self.tree.addTopLevelItem(root)
        self.tree.expandAll()
        self.tree.itemDoubleClicked.connect(self.on_tree_double)
        sb_layout.addWidget(self.tree)

        # Theme controls
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Escuro", "dark")
        self.theme_combo.addItem("Claro", "light")
        self.theme_combo.setCurrentIndex(0 if settings.theme == 'dark' else 1)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_change)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        sb_layout.addLayout(theme_layout)

        sb_layout.addStretch()

        splitter.addWidget(sidebar)

        # Right: content with tabs
        content = QWidget()
        content.setObjectName('ContentFrame')
        content_layout = QVBoxLayout(content)

        toolbar = QToolBar()
        self.btn_new_tab = QAction('Novo Iframe', self)
        toolbar.addAction(self.btn_new_tab)
        self.btn_new_tab.triggered.connect(self.on_new_iframe)
        content_layout.addWidget(toolbar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.on_tab_close)

        # Dashboard, Kanban, Table
        self.tab_dashboard = QWidget()
        self.tab_kanban = QWidget()
        self.tab_table = QWidget()

        self.tabs.addTab(self.tab_dashboard, '📊 Dashboard')
        self.tabs.addTab(self.tab_kanban, '📋 Kanban')
        self.tabs.addTab(self.tab_table, '📄 Detalhes')
        content_layout.addWidget(self.tabs)

        splitter.addWidget(content)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # build tabs content
        self._build_dashboard_tab()
        self._build_kanban_tab()
        self._build_table_tab()

        # apply theme
        self.apply_theme(settings.theme)

    def apply_theme(self, theme_name: str):
        self.setStyleSheet(DARK_STYLE if theme_name == 'dark' else LIGHT_STYLE)

    # ---------------- UI builders ----------------
    def _build_dashboard_tab(self):
        layout = QVBoxLayout(self.tab_dashboard)
        grid = QGridLayout()
        self.stat_cards = {}
        stats = [('total', 'Total', '#3498db'), ('pendentes', 'Pendentes', '#e74c3c'), ('concluidos', 'Concluídos', '#2ecc71')]
        for i, (k, label, color) in enumerate(stats):
            frame = QFrame()
            frame.setStyleSheet(f'background-color: {color}; padding: 12px; border-radius: 8px; color: white;')
            f_layout = QVBoxLayout(frame)
            f_layout.addWidget(QLabel(label))
            v = QLabel('0')
            v.setFont(QFont('Arial', 20, QFont.Bold))
            v.setObjectName('value')
            f_layout.addWidget(v)
            grid.addWidget(frame, i // 2, i % 2)
            self.stat_cards[k] = frame
        layout.addLayout(grid)

        # web area for charts
        if WEB_AVAILABLE:
            self.web_charts = QWebEngineView()
            self.web_charts.setMinimumHeight(300)
            layout.addWidget(self.web_charts)
        else:
            self.web_charts = QTextBrowser()
            self.web_charts.setHtml('<h3>WebEngine não disponível - instalação opcional</h3>')
            layout.addWidget(self.web_charts)

    def _build_kanban_tab(self):
        layout = QHBoxLayout(self.tab_kanban)
        self.kanban_columns = {}
        for status in ['Pendente', 'Em Andamento', 'Concluído']:
            col = QListWidget()
            layout.addWidget(col)
            self.kanban_columns[status] = col

    def _build_table_tab(self):
        layout = QVBoxLayout(self.tab_table)
        self.table = QTableWidget()
        layout.addWidget(self.table)

    # ---------------- Actions ----------------
    def load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Selecionar arquivo Excel', '', 'Excel Files (*.xlsx *.xls);;CSV Files (*.csv)')
        if not filepath:
            return
        import requests
        try:
            resp = requests.post('http://127.0.0.1:5000/api/load', json={'filepath': filepath})
            if resp.ok and resp.json().get('success'):
                sheets = resp.json().get('sheets', [])
                QMessageBox.information(self, 'Sucesso', 'Arquivo carregado com sucesso')
                self.update_data()
            else:
                QMessageBox.critical(self, 'Erro', 'Falha ao carregar arquivo')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao chamar backend: {e}')

    def apply_filters(self, sheet=None, responsavel=None, status=None, ressalva=None):
        import requests
        payload = {}
        if sheet: payload['sheet'] = sheet
        if responsavel: payload['responsavel'] = responsavel
        if status: payload['status'] = status
        if ressalva: payload['ressalva'] = ressalva
        try:
            requests.post('http://127.0.0.1:5000/api/filter', json=payload)
            self.update_data()
        except Exception as e:
            print('Erro ao aplicar filtros', e)

    def update_data(self):
        import requests
        try:
            stats = requests.get('http://127.0.0.1:5000/api/statistics').json()
            for k, frame in self.stat_cards.items():
                label = frame.findChild(QLabel, 'value')
                # original frames store QLabel 'value' — if missing just update via layout
                if label:
                    label.setText(str(stats.get(k, 0)))
            data_resp = requests.get('http://127.0.0.1:5000/api/data').json()
            rows = data_resp.get('data', [])
            if rows:
                cols = list(rows[0].keys())
                self.table.setColumnCount(len(cols))
                self.table.setHorizontalHeaderLabels(cols)
                self.table.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    for j, col in enumerate(cols):
                        self.table.setItem(i, j, QTableWidgetItem(str(row.get(col, ''))))
                self.table.resizeColumnsToContents()
            # update charts
            self.update_charts()
        except Exception as e:
            print('Erro ao atualizar dados', e)

    def update_charts(self):
        # simple html placeholder
        html = """
        <!doctype html><html><head><meta charset='utf-8'></head><body><h3>Gráficos</h3></body></html>
        """
        if WEB_AVAILABLE and isinstance(self.web_charts, QWebEngineView):
            self.web_charts.setHtml(html)
        else:
            self.web_charts.setHtml('<p>Instale PySide6-WebEngine para gráficos embutidos.</p>')

    def export_data(self):
        import requests
        try:
            r = requests.get('http://127.0.0.1:5000/api/export')
            if r.ok and r.json().get('success'):
                QMessageBox.information(self, 'Exportado', f"Arquivo salvo em: {r.json().get('filepath')}")
            else:
                QMessageBox.warning(self, 'Exportar', 'Nenhum dado para exportar')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao exportar: {e}')

    # tree actions
    def on_tree_double(self, item, col):
        title = item.text(0)
        # if tab exists, select, else create simple tab
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == title:
                self.tabs.setCurrentIndex(i)
                return
        w = QTextBrowser()
        w.setHtml(f"<h2>{title}</h2><p>Conteúdo do nó.</p>")
        self.tabs.addTab(w, title)
        self.tabs.setCurrentWidget(w)

    def on_new_iframe(self):
        title, ok = QInputDialog.getText(self, 'Nova Aba', 'Título:')
        if not ok or not title.strip():
            return
        url, ok2 = QInputDialog.getText(self, 'Nova Aba', 'URL (opcional):')
        w = QWebEngineView() if (WEB_AVAILABLE and url.strip()) else QTextBrowser()
        if url.strip() and WEB_AVAILABLE:
            try:
                w.load(url)
            except Exception:
                w.setHtml('<p>Falha ao carregar URL</p>')
        else:
            w.setHtml(f"<h2>{title}</h2><p>Iframe local.</p>")
        self.tabs.addTab(w, title)
        self.tabs.setCurrentWidget(w)

    def on_tab_close(self, idx):
        self.tabs.removeTab(idx)

    def on_theme_change(self, index):
        theme = self.theme_combo.itemData(index)
        self.settings.theme = theme
        self.apply_theme(theme)


def setup_logging():
    log_file = Path(__file__).parent / 'merged_app.log'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler(log_file, 'w'), logging.StreamHandler(sys.stdout)])


def main():
    setup_logging()

    # start flask backend thread
    flask_thread = FlaskThread()
    flask_thread.start()

    # start Qt app
    app = QApplication(sys.argv)
    settings = SettingsModel()
    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
