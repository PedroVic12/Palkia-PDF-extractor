"""
main.py - Sistema de Controle e Gestão MUST e Atividades SP

Arquitetura MVC com PySide6
- Menu lateral em árvore
- Tabs para cada funcionalidade
- Integração com banco de dados
- Geração de PDF e relatórios

Requisitos:
pip install PySide6 PySide6-WebEngine pandas plotly weasyprint flask pyodbc ansi2html sqlite3
"""

from __future__ import annotations
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QTabWidget, QToolBar,
    QTextBrowser, QInputDialog, QMessageBox, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QFont

# Imports opcionais com fallback
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEB_AVAILABLE = True
except ImportError:
    QWebEngineView = None
    WEB_AVAILABLE = False
    print("AVISO: PySide6-WebEngine não instalado. Funcionalidades web limitadas.")

try:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    PANDAS_AVAILABLE = True
except ImportError:
    pd = px = go = None
    PANDAS_AVAILABLE = False
    print("AVISO: pandas/plotly não instalados. Dashboards desabilitados.")

try:
    from weasyprint import HTML
    import io
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    HTML = io = None
    WEASYPRINT_AVAILABLE = False
    print(f"AVISO: weasyprint e/ou suas dependências não instalados. Geração de PDF desabilitada. Erro: {e}")

try:
    import sqlite3
    import pyodbc
    DB_AVAILABLE = True
except ImportError:
    sqlite3 = pyodbc = None
    DB_AVAILABLE = False
    print("AVISO: Drivers de banco de dados não instalados.")

# Importação do módulo Palkia (deve estar no mesmo diretório)
try:
    from Palkia_GUI import PalkiaWindowGUI
    PALKIA_AVAILABLE = True
except ImportError:
    PalkiaWindowGUI = None
    PALKIA_AVAILABLE = False
    print("AVISO: Palkia_GUI.py não encontrado.")

# Importação de estilos
try:
    from styles import STYLESHEET, APP_STYLES
except ImportError:
    STYLESHEET = """
        QWidget { 
            background-color: #111827; 
            color: #F9FAFB; 
            font-family: 'Segoe UI', Arial;
            font-size: 13px;
        }
        #Sidebar { 
            background-color: #1F2937; 
            border-right: 1px solid #374151; 
        }
        QTreeWidget {
            background-color: #1F2937;
            border: 1px solid #374151;
            border-radius: 6px;
            padding: 4px;
        }
        QTreeWidget::item {
            padding: 8px;
            border-radius: 4px;
        }
        QTreeWidget::item:hover {
            background-color: #374151;
        }
        QTreeWidget::item:selected {
            background-color: #3B82F6;
        }
        QPushButton {
            background-color: #3B82F6;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #2563EB;
        }
        QPushButton:pressed {
            background-color: #1D4ED8;
        }
        QTabWidget::pane {
            border: 1px solid #374151;
            border-radius: 6px;
            background-color: #1F2937;
        }
        QTabBar::tab {
            background-color: #374151;
            color: #D1D5DB;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        QTabBar::tab:selected {
            background-color: #3B82F6;
            color: white;
        }
        QTabBar::tab:hover {
            background-color: #4B5563;
        }
        QToolBar {
            background-color: #1F2937;
            border: none;
            padding: 8px;
        }
        QLabel {
            color: #F9FAFB;
        }
    """
    APP_STYLES = STYLESHEET


# ==================== MODEL ====================
class AppModel(QObject):
    """Modelo de dados da aplicação"""
    
    pages_changed = Signal()
    data_loaded = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._pages: List[Dict] = []
        self._db_connection = None
        self._current_data = {}
        
    def add_page(self, title: str, widget_type: str, data: Optional[Dict] = None):
        """Adiciona uma nova página/tab"""
        page = {
            "title": title,
            "widget_type": widget_type,
            "data": data or {}
        }
        self._pages.append(page)
        self.pages_changed.emit()
        
    def remove_page(self, index: int):
        """Remove uma página pelo índice"""
        if 0 <= index < len(self._pages):
            del self._pages[index]
            self.pages_changed.emit()
            
    def get_pages(self) -> List[Dict]:
        """Retorna todas as páginas"""
        return list(self._pages)
    
    def init_database(self, db_path: str = "must_database.db"):
        """Inicializa conexão com banco de dados SQLite"""
        if not DB_AVAILABLE:
            self.error_occurred.emit("SQLite não disponível")
            return False
            
        try:
            self._db_connection = sqlite3.connect(db_path)
            self._create_tables()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Erro ao conectar BD: {str(e)}")
            return False
    
    def _create_tables(self):
        """Cria tabelas necessárias"""
        if not self._db_connection:
            return
            
        cursor = self._db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atividades_sp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa TEXT,
                ponto TEXT,
                data_solicitacao DATE,
                status TEXT,
                aprovado BOOLEAN,
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._db_connection.commit()
    
    def load_must_data(self):
        """Carrega dados de MUST do banco"""
        if not self._db_connection:
            self.error_occurred.emit("Banco não conectado")
            return
            
        try:
            query = "SELECT * FROM atividades_sp ORDER BY data_solicitacao DESC"
            if PANDAS_AVAILABLE:
                df = pd.read_sql_query(query, self._db_connection)
                self._current_data = {"must_data": df}
                self.data_loaded.emit(self._current_data)
            else:
                cursor = self._db_connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                self._current_data = {"must_data": rows}
                self.data_loaded.emit(self._current_data)
        except Exception as e:
            self.error_occurred.emit(f"Erro ao carregar dados: {str(e)}")


# ==================== VIEW ====================
class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    create_tab_requested = Signal(str, str)  # title, type
    close_tab_requested = Signal(int)
    tree_item_opened = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Controle e Gestão - MUST e Atividades SP")
        self.resize(1400, 800)
        
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== SIDEBAR =====
        self._create_sidebar(main_layout)
        
        # ===== ÁREA PRINCIPAL =====
        self._create_main_area(main_layout)
        
        # Aplicar tema
        self.setStyleSheet(STYLESHEET)
        
    def _create_sidebar(self, parent_layout):
        """Cria sidebar com menu em árvore"""
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(12)
        
        # Logo/Título
        title_label = QLabel("📊 Sistema MUST")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        # Árvore de navegação
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self._populate_tree()
        sidebar_layout.addWidget(self.tree)
        
        # Botões de ação
        self.btn_novo_tab = QPushButton("➕ Nova Aba")
        sidebar_layout.addWidget(self.btn_novo_tab)
        
        self.btn_atualizar = QPushButton("🔄 Atualizar Dados")
        sidebar_layout.addWidget(self.btn_atualizar)
        
        sidebar_layout.addStretch()
        
        # Conexões
        self.tree.itemDoubleClicked.connect(self._on_tree_double_click)
        self.btn_novo_tab.clicked.connect(self._on_new_tab_clicked)
        
        parent_layout.addWidget(self.sidebar)
    
    def _populate_tree(self):
        """Popula árvore de navegação"""
        # Dashboard
        dashboard_item = QTreeWidgetItem(["📊 Dashboards"])
        dashboard_item.addChild(QTreeWidgetItem(["Dashboard MUST"]))
        dashboard_item.addChild(QTreeWidgetItem(["Dashboard Atividades SP"]))
        dashboard_item.addChild(QTreeWidgetItem(["Relatórios Gerenciais"]))
        
        # Ferramentas
        tools_item = QTreeWidgetItem(["🛠️ Ferramentas"])
        tools_item.addChild(QTreeWidgetItem(["Palkia Extractor"]))
        tools_item.addChild(QTreeWidgetItem(["Deck Builder"]))
        tools_item.addChild(QTreeWidgetItem(["Organizador de Arquivos"]))
        tools_item.addChild(QTreeWidgetItem(["Análise de Contingências"]))
        
        # Relatórios
        reports_item = QTreeWidgetItem(["📄 Relatórios"])
        reports_item.addChild(QTreeWidgetItem(["Gerar Relatório PDF"]))
        reports_item.addChild(QTreeWidgetItem(["Histórico de Análises"]))
        
        # Configurações
        config_item = QTreeWidgetItem(["⚙️ Configurações"])
        config_item.addChild(QTreeWidgetItem(["Banco de Dados"]))
        config_item.addChild(QTreeWidgetItem(["Importar/Exportar"]))
        
        self.tree.addTopLevelItems([dashboard_item, tools_item, reports_item, config_item])
        self.tree.expandAll()
    
    def _create_main_area(self, parent_layout):
        """Cria área principal com tabs"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(8)
        
        # Toolbar
        toolbar = QToolBar()
        self.status_label = QLabel("✅ Sistema inicializado")
        self.status_label.setStyleSheet("color: #10B981; font-weight: 600;")
        toolbar.addWidget(self.status_label)
        
        toolbar.addWidget(QWidget())  # Spacer
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        toolbar.addWidget(self.progress_bar)
        
        right_layout.addWidget(toolbar)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._on_tab_close_requested)
        right_layout.addWidget(self.tabs, 1)
        
        parent_layout.addWidget(right_widget, 1)
    
    def add_tab(self, widget: QWidget, title: str):
        """Adiciona uma nova tab"""
        index = self.tabs.addTab(widget, title)
        self.tabs.setCurrentIndex(index)
        self.status_label.setText(f"📂 Aberto: {title}")
    
    def _on_tree_double_click(self, item: QTreeWidgetItem, column: int):
        """Handler para duplo clique na árvore"""
        item_text = item.text(0)
        self.tree_item_opened.emit(item_text)
    
    def _on_new_tab_clicked(self):
        """Handler para botão de nova aba"""
        title, ok = QInputDialog.getText(self, "Nova Aba", "Título da aba:")
        if ok and title.strip():
            self.create_tab_requested.emit(title.strip(), "text")
    
    def _on_tab_close_requested(self, index: int):
        """Handler para fechar tab"""
        self.close_tab_requested.emit(index)
    
    def show_message(self, message: str, error: bool = False):
        """Mostra mensagem na barra de status"""
        if error:
            self.status_label.setText(f"❌ {message}")
            self.status_label.setStyleSheet("color: #EF4444; font-weight: 600;")
        else:
            self.status_label.setText(f"✅ {message}")
            self.status_label.setStyleSheet("color: #10B981; font-weight: 600;")


# ==================== CONTROLLER ====================
class AppController:
    """Controlador principal da aplicação"""
    
    def __init__(self, model: AppModel, view: MainWindow):
        self.model = model
        self.view = view
        
        # Conectar sinais
        self.view.create_tab_requested.connect(self.handle_create_tab)
        self.view.close_tab_requested.connect(self.handle_close_tab)
        self.view.tree_item_opened.connect(self.handle_tree_item)
        self.model.pages_changed.connect(self.sync_tabs)
        self.model.error_occurred.connect(lambda msg: self.view.show_message(msg, error=True))
        self.model.data_loaded.connect(self.handle_data_loaded)
        
        # Inicializar banco de dados
        self.model.init_database()
    
    def handle_create_tab(self, title: str, widget_type: str):
        """Cria nova tab"""
        self.model.add_page(title, widget_type)
    
    def handle_close_tab(self, index: int):
        """Fecha tab"""
        self.model.remove_page(index)
    
    def handle_tree_item(self, item_name: str):
        """Manipula abertura de item da árvore"""
        # Verificar se já existe tab aberta
        for idx in range(self.view.tabs.count()):
            if self.view.tabs.tabText(idx) == item_name:
                self.view.tabs.setCurrentIndex(idx)
                return
        
        # Criar widget baseado no tipo
        widget = self._create_widget_for_item(item_name)
        if widget:
            self.model.add_page(item_name, "custom", {"widget": widget})
    
    def _create_widget_for_item(self, item_name: str) -> Optional[QWidget]:
        """Cria widget apropriado para cada item"""
        
        if "Dashboard MUST" in item_name:
            return self._create_dashboard_widget()
        
        elif "Palkia Extractor" in item_name:
            if PALKIA_AVAILABLE:
                return PalkiaWindowGUI()
            else:
                widget = QLabel("⚠️ Palkia_GUI.py não encontrado")
                widget.setAlignment(Qt.AlignCenter)
                return widget
        
        elif "Gerar Relatório PDF" in item_name:
            return self._create_pdf_generator_widget()
        
        elif "Banco de Dados" in item_name:
            return self._create_database_widget()
        
        else:
            # Widget padrão
            text_widget = QTextBrowser()
            text_widget.setHtml(f"<h2>{item_name}</h2><p>Funcionalidade em desenvolvimento...</p>")
            return text_widget
    
    def _create_dashboard_widget(self) -> QWidget:
        """Cria widget de dashboard"""
        if WEB_AVAILABLE and PANDAS_AVAILABLE:
            web_view = QWebEngineView()
            
            # Gerar gráfico de exemplo
            try:
                df = pd.DataFrame({
                    'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
                    'Aprovados': [45, 52, 48, 61, 58],
                    'Rejeitados': [5, 8, 6, 4, 7]
                })
                
                fig = px.bar(df, x='Mês', y=['Aprovados', 'Rejeitados'], 
                            title='Análise Mensal de MUST',
                            barmode='group')
                fig.update_layout(template='plotly_dark')
                
                html_content = fig.to_html(include_plotlyjs='cdn')
                web_view.setHtml(html_content)
            except Exception as e:
                web_view.setHtml(f"<h3>Erro ao gerar gráfico: {str(e)}</h3>")
            
            return web_view
        else:
            label = QLabel("⚠️ Dashboard requer PySide6-WebEngine e pandas")
            label.setAlignment(Qt.AlignCenter)
            return label
    
    def _create_pdf_generator_widget(self) -> QWidget:
        """Cria widget para geração de PDF"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("<h2>📄 Gerador de Relatórios PDF</h2>"))
        
        btn_generate = QPushButton("Gerar PDF de Análise")
        btn_generate.clicked.connect(self._generate_pdf_report)
        layout.addWidget(btn_generate)
        
        self.pdf_preview = QTextBrowser()
        layout.addWidget(self.pdf_preview)
        
        layout.addStretch()
        return widget
    
    def _create_database_widget(self) -> QWidget:
        """Cria widget de configuração de BD"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("<h2>💾 Configuração de Banco de Dados</h2>"))
        
        btn_load = QPushButton("Carregar Dados MUST")
        btn_load.clicked.connect(lambda: self.model.load_must_data())
        layout.addWidget(btn_load)
        
        btn_import = QPushButton("Importar Excel")
        btn_import.clicked.connect(self._import_excel)
        layout.addWidget(btn_import)
        
        layout.addStretch()
        return widget
    
    def _generate_pdf_report(self):
        """Gera relatório em PDF"""
        if not WEASYPRINT_AVAILABLE:
            self.view.show_message("WeasyPrint não instalado", error=True)
            return
        
        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial; margin: 40px; }
                    h1 { color: #2563EB; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #3B82F6; color: white; }
                </style>
            </head>
            <body>
                <h1>Relatório de Análise MUST</h1>
                <p><strong>Data:</strong> {}</p>
                <h2>Resumo de Atividades</h2>
                <table>
                    <tr><th>Empresa</th><th>Status</th><th>Aprovado</th></tr>
                    <tr><td>Empresa A</td><td>Concluído</td><td>Sim</td></tr>
                    <tr><td>Empresa B</td><td>Em análise</td><td>Não</td></tr>
                </table>
            </body>
            </html>
            """.format(datetime.now().strftime("%d/%m/%Y %H:%M"))
            
            # Salvar PDF
            file_path, _ = QFileDialog.getSaveFileName(
                self.view, "Salvar Relatório", "", "PDF Files (*.pdf)"
            )
            
            if file_path:
                HTML(string=html_content).write_pdf(file_path)
                self.view.show_message(f"PDF salvo em: {file_path}")
                self.pdf_preview.setHtml(html_content)
        
        except Exception as e:
            self.view.show_message(f"Erro ao gerar PDF: {str(e)}", error=True)
    
    def _import_excel(self):
        """Importa dados de arquivo Excel"""
        if not PANDAS_AVAILABLE:
            self.view.show_message("pandas não instalado", error=True)
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Selecionar Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.view.show_message(f"Importado {len(df)} registros")
                # Aqui você implementaria a lógica de inserção no BD
            except Exception as e:
                self.view.show_message(f"Erro ao importar: {str(e)}", error=True)
    
    def handle_data_loaded(self, data: Dict):
        """Manipula dados carregados"""
        self.view.show_message("Dados carregados com sucesso")
    
    def sync_tabs(self):
        """Sincroniza tabs com o modelo"""
        # Limpar todas as tabs
        self.view.tabs.clear()
        
        # Recriar tabs baseado no modelo
        for page in self.model.get_pages():
            title = page.get("title", "Sem título")
            widget_type = page.get("widget_type", "text")
            data = page.get("data", {})
            
            if "widget" in data:
                widget = data["widget"]
            elif widget_type == "web" and WEB_AVAILABLE:
                widget = QWebEngineView()
            else:
                widget = QTextBrowser()
                widget.setHtml(f"<h2>{title}</h2>")
            
            self.view.add_tab(widget, title)


# ==================== MAIN ====================
def main():
    """Função principal"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Criar MVC
    model = AppModel()
    view = MainWindow()
    controller = AppController(model, view)
    
    # Mostrar janela
    view.show()
    
    # Executar aplicação
    sys.exit(app.exec())


if __name__ == '__main__':
    main()