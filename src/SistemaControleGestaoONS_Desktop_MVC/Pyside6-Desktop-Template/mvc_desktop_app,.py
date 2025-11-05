# -*- coding: utf-8 -*-
"""
main.py

Aplicação Principal Unificada - Sistema de Controle e Gestão (ONS 2025)
Arquitetura: MVC (Model-View-Controller)
UI: PySide6, com Menu em Árvore e Abas (QTabWidget)

Este arquivo contém TODO o código da aplicação, incluindo módulos 
integrados (como Palkia_GUI) e estilos (QSS) para ser um 
único script executável.
"""
from __future__ import annotations
import sys
import os
import re
import sqlite3
import pyodbc
import webbrowser
import tempfile
import io
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# ==============================================================================
# 1. IMPORTAÇÃO DE DEPENDÊNCIAS PRINCIPAIS (PySide6)
# ==============================================================================
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, QPushButton, QTabWidget, QToolBar,
    QTextBrowser, QInputDialog, QMessageBox, QAction, QLineEdit, QLabel,
    QFrame, QGridLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QDialog, QProgressBar, QStackedWidget,
    QFileDialog, QTextEdit, QSizePolicy, QGroupBox, QTableView,
    QAbstractButton, QListWidget, QListWidgetItem
)
from PySide6.QtCore import (
    Qt, Signal, QObject, QUrl, QSize, Slot, QThread, QAbstractTableModel,
    QPoint, QRect, QRectF, Property, QPropertyAnimation, QEasingCurve
)
from PySide6.QtGui import (
    QFont, QIcon, QColor, QPainter, QPixmap
)

# ==============================================================================
# 2. IMPORTAÇÃO DE DEPENDÊNCIAS OPCIONAIS (com try...except)
# ==============================================================================
# Isso permite que o app abra mesmo se algo estiver faltando

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    HAVE_WEB_ENGINE = True
except ImportError:
    QWebEngineView = None # type: ignore
    HAVE_WEB_ENGINE = False
    print("AVISO: PySide6-WebEngine não instalado. Dashboards estarão desabilitados.")

try:
    import pandas as pd
    HAVE_PANDAS = True
except ImportError:
    pd = None # type: ignore
    HAVE_PANDAS = False
    print("AVISO: Pandas não instalado. Funcionalidades de dados estarão desabilitadas.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAVE_PLOTLY = True
except ImportError:
    go = px = None # type: ignore
    HAVE_PLOTLY = False
    print("AVISO: Plotly não instalado. Geração de gráficos estará desabilitada.")

try:
    import pyodbc
    HAVE_PYODBC = True
except ImportError:
    pyodbc = None # type: ignore
    HAVE_PYODBC = False
    print("AVISO: pyodbc não instalado. Conexão com SQL Server estará desabilitada.")

try:
    from weasyprint import HTML
    HAVE_WEASYPRINT = True
except ImportError:
    HTML = None # type: ignore
    HAVE_WEASYPRINT = False
    print("AVISO: WeasyPrint não instalado. Geração de relatórios PDF estará desabilitada.")

try:
    from ansi2html import Ansi2HTMLConverter
    ansi_converter = Ansi2HTMLConverter(dark_bg=True, scheme="xterm")
    HAVE_ANSI2HTML = True
except ImportError:
    ansi_converter = None
    HAVE_ANSI2HTML = False
    print("AVISO: 'ansi2html' não instalado. Os logs não serão coloridos.")


# ==============================================================================
# 3. ESTILOS QSS (Dark/Light Mode)
# ==============================================================================

# Estilo DARK (baseado no styles.py fornecido)
DARK_STYLE = """
    QWidget {
        background-color: #2b2b2b; color: #f0f0f0; font-family: "Segoe UI", sans-serif; font-size: 10pt;
    }
    QMainWindow { background-color: #212121; }
    QGroupBox {
        font-weight: bold; border: 1px solid #444; border-radius: 8px; margin-top: 10px; padding: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; color: #f0f0f0;
    }
    QPushButton {
        background-color: #3c3f41; color: #f0f0f0; border: 1px solid #555;
        padding: 8px 16px; border-radius: 4px; font-weight: bold;
    }
    QPushButton:hover { background-color: #4f5355; }
    QPushButton:pressed { background-color: #2a2d2f; }
    
    /* Botões Palkia */
    QPushButton#run_button { background-color: #007acc; }
    QPushButton#run_button:hover { background-color: #008ae6; }
    QPushButton#export_excel { background-color: #9CCC65; }

    QLineEdit, QTextEdit {
        background-color: #333; color: #f0f0f0; border: 1px solid #555;
        border-radius: 4px; padding: 6px;
    }
    QLineEdit:focus, QTextEdit:focus { border: 1px solid #007acc; }

    QTableView { background-color: #333; gridline-color: #444; }
    QHeaderView::section {
        background-color: #3c3f41; color: #f0f0f0; padding: 6px;
        border: 1px solid #444; font-weight: bold;
    }
    
    /* --- Estilos do Template MVC --- */
    QToolBar {
        background-color: #3c3f41; /* Fundo da barra de ferramentas */
        border-bottom: 1px solid #444;
    }
    QToolBar QToolButton { padding: 8px; border-radius: 4px; }
    QToolBar QToolButton:hover { background-color: #4f5355; }
    
    /* Menu lateral (Árvore) */
    QTreeWidget {
        background-color: #2b2b2b;
        border: none;
        padding-top: 10px;
    }
    QTreeWidget::item { padding: 8px 12px; border-radius: 4px; }
    QTreeWidget::item:selected, QTreeWidget::item:selected:active {
        background-color: #007acc; /* Destaque azul */
        color: white;
    }
    QTreeWidget::item:hover { background-color: #3c3f41; }
    
    /* Abas centrais (Tabs) */
    QTabWidget::pane {
        border: none;
        background-color: #212121; /* Fundo da área da aba */
    }
    QTabBar::tab {
        background-color: #2b2b2b;
        color: #f0f0f0;
        padding: 10px 15px;
        border: 1px solid #212121;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #007acc; /* Aba ativa */
        color: white;
    }
    QTabBar::tab:!selected { background-color: #3c3f41; } /* Aba inativa */
    QTabBar::tab:hover { background-color: #4f5355; }
"""

# Estilo LIGHT (baseado no template anterior)
LIGHT_STYLE = """
    QWidget {
        background-color: #f0f2f5; /* Fundo principal claro */
        color: #1f1f1f; /* Texto principal escuro */
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 10pt;
    }
    QMainWindow { background-color: #e4e7eb; }
    QGroupBox {
        font-weight: bold; border: 1px solid #dcdcdc; border-radius: 8px; margin-top: 10px; padding: 15px;
    }
    QGroupBox::title {
        subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; color: #1f1f1f;
    }
    QPushButton {
        background-color: #0078d4; color: white; border: none;
        padding: 8px 16px; border-radius: 4px; font-weight: bold;
    }
    QPushButton:hover { background-color: #005a9e; }
    QPushButton:pressed { background-color: #004578; }
    
    /* Botões Palkia */
    QPushButton#run_button { background-color: #0078d4; }
    QPushButton#run_button:hover { background-color: #005a9e; }
    QPushButton#export_excel { background-color: #4CAF50; }
    QPushButton#export_excel:hover { background-color: #45a049; }

    QLineEdit, QTextEdit {
        background-color: #ffffff; color: #1f1f1f; border: 1px solid #dcdcdc;
        border-radius: 4px; padding: 6px;
    }
    QLineEdit:focus, QTextEdit:focus { border: 1px solid #0078d4; }
    
    QTableView { background-color: #ffffff; gridline-color: #e0e0e0; }
    QHeaderView::section {
        background-color: #f0f2f5; color: #1f1f1f; padding: 6px;
        border: 1px solid #dcdcdc; font-weight: bold;
    }

    /* --- Estilos do Template MVC --- */
    QToolBar {
        background-color: #ffffff;
        border-bottom: 1px solid #dcdcdc;
    }
    QToolBar QToolButton { padding: 8px; border-radius: 4px; }
    QToolBar QToolButton:hover { background-color: #f0f2f5; }
    
    /* Menu lateral (Árvore) */
    QTreeWidget {
        background-color: #ffffff;
        border: none;
        padding-top: 10px;
    }
    QTreeWidget::item { padding: 8px 12px; border-radius: 4px; }
    QTreeWidget::item:selected, QTreeWidget::item:selected:active {
        background-color: #0078d4; /* Destaque azul */
        color: white;
    }
    QTreeWidget::item:hover { background-color: #f0f2f5; }

    /* Abas centrais (Tabs) */
    QTabWidget::pane {
        border: none;
        background-color: #e4e7eb; /* Fundo da área da aba */
    }
    QTabBar::tab {
        background-color: #ffffff; color: #1f1f1f;
        padding: 10px 15px; border: 1px solid #e4e7eb; border-bottom: none;
        border-top-left-radius: 4px; border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #0078d4; /* Aba ativa */
        color: white; border-bottom: 1px solid #0078d4;
    }
    QTabBar::tab:!selected { background-color: #f0f2f5; } /* Aba inativa */
    QTabBar::tab:hover { background-color: #dcdcdc; }
"""

# ==============================================================================
# 4. CÓDIGO DO MÓDULO Palkia_GUI.py (INTEGRADO)
# ==============================================================================

# --- Início do Palkia_GUI.py ---

# Tenta importar o script run.py principal com a automação do ETL
try:
    import run as run_script
    HAVE_RUN_SCRIPT = True
except ImportError as e:
    HAVE_RUN_SCRIPT = False
    print(f"AVISO (Módulo Palkia): Não foi possível importar 'run.py'. Detalhes: {e}")
    print("         A funcionalidade de execução do ETL Palkia estará desabilitada.")

class PandasModel(QAbstractTableModel):
    """Modelo Qt para exibir DataFrames do Pandas."""
    def __init__(self, data):
        super().__init__()
        self._data = data
    def rowCount(self, parent=None): return self._data.shape[0]
    def columnCount(self, parent=None): return self._data.shape[1]
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None

class Worker(QObject):
    """Worker para executar tarefas (ETL) em uma thread separada."""
    finished = Signal()
    progress = Signal(str)
    table_ready = Signal(str, pd.DataFrame)
    error = Signal(str)

    def __init__(self, selected_folder, run_mode):
        super().__init__()
        self.selected_folder = selected_folder
        self.run_mode = run_mode
        self.is_running = True

    def run(self):
        """Executa a lógica do ETL."""
        if not HAVE_RUN_SCRIPT:
            self.error.emit("Erro Crítico: 'run.py' não foi encontrado. Não é possível executar o ETL.")
            self.finished.emit()
            return
            
        try:
            # Redireciona stdout para capturar logs
            stdout_capture = io.StringIO()
            sys.stdout = stdout_capture
            
            # Delega a lógica principal para o script 'run.py' importado
            if self.run_mode == 'tables':
                self.progress.emit("Iniciando 'processar_tabelas_pvrv'...")
                run_script.processar_tabelas_pvrv(self.selected_folder, self.progress.emit)
                self.progress.emit("Extração de tabelas concluída.")
                
            elif self.run_mode == 'text':
                self.progress.emit("Iniciando 'processar_textos_pvrv'...")
                run_script.processar_textos_pvrv(self.selected_folder, self.progress.emit)
                self.progress.emit("Extração de textos concluída.")
                
            elif self.run_mode == 'consolidate':
                self.progress.emit("Iniciando 'consolidar_dados'...")
                dfs = run_script.consolidar_dados(self.selected_folder, self.progress.emit)
                
                if not dfs:
                    self.progress.emit("Nenhum dado consolidado gerado.")
                    self.error.emit("Nenhum dado consolidado foi retornado pelo script.")
                else:
                    self.progress.emit(f"Consolidação concluída. {len(dfs)} tabelas geradas.")
                    for df_name, df_data in dfs.items():
                        if isinstance(df_data, pd.DataFrame):
                            self.table_ready.emit(df_name, df_data)
                        else:
                            self.progress.emit(f"Aviso: item '{df_name}' retornado não é um DataFrame.")
            
            # Restaura stdout
            sys.stdout = sys.__stdout__
            
            # Envia o log capturado
            log_content = stdout_capture.getvalue()
            self.progress.emit(f"\n--- Log do Script (stdout) ---\n{log_content}")
            
        except Exception as e:
            sys.stdout = sys.__stdout__ # Garante restauração em caso de erro
            error_msg = f"Erro durante a execução do worker: {e}\nLog: {stdout_capture.getvalue()}"
            self.error.emit(error_msg)
            
        finally:
            self.finished.emit()

class PalkiaWindowGUI(QWidget):
    """Widget principal para a interface do Palkia ETL."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Palkia - PVRV Extractor GUI")
        # self.setStyleSheet(APP_STYLES) # Não é mais necessário, o estilo é global
        self.thread = None
        self.worker = None
        self.selected_folder = ""
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 1. Grupo de Seleção de Pasta
        folder_group = QGroupBox("Seleção de Pasta")
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("Selecionar Pasta PVRV")
        self.folder_button.clicked.connect(self.select_folder)
        self.folder_label = QLineEdit("Nenhuma pasta selecionada")
        self.folder_label.setReadOnly(True)
        folder_layout.addWidget(self.folder_button)
        folder_layout.addWidget(self.folder_label, 1)
        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)

        # 2. Grupo de Ações
        actions_group = QGroupBox("Ações de Extração")
        actions_layout = QHBoxLayout()
        self.run_tables_button = QPushButton("Extrair Tabelas")
        self.run_tables_button.setObjectName("run_button")
        self.run_tables_button.clicked.connect(lambda: self.run_worker('tables'))
        self.run_text_button = QPushButton("Extrair Textos")
        self.run_text_button.setObjectName("run_button")
        self.run_text_button.clicked.connect(lambda: self.run_worker('text'))
        self.run_consolidate_button = QPushButton("Consolidar Dados")
        self.run_consolidate_button.setObjectName("run_button")
        self.run_consolidate_button.clicked.connect(lambda: self.run_worker('consolidate'))
        
        actions_layout.addWidget(self.run_tables_button)
        actions_layout.addWidget(self.run_text_button)
        actions_layout.addWidget(self.run_consolidate_button)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        # 3. Abas de Saída (Logs e Tabelas)
        self.output_tabs = QTabWidget()
        
        # Aba de Logs
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        self.log_browser = QTextEdit()
        self.log_browser.setReadOnly(True)
        self.log_browser.setFont(QFont("Courier New", 9))
        self.log_browser.setPlaceholderText("Logs da execução aparecerão aqui...")
        log_layout.addWidget(self.log_browser)
        self.output_tabs.addTab(log_widget, "Log de Execução")
        
        # Aba de Tabelas (inicialmente vazia)
        self.tables_tab_widget = QTabWidget()
        self.tables_tab_widget.setTabsClosable(True)
        self.tables_tab_widget.tabCloseRequested.connect(self.tables_tab_widget.removeTab)
        self.output_tabs.addTab(self.tables_tab_widget, "Tabelas Consolidadas")
        
        main_layout.addWidget(self.output_tabs, 1) # Expande verticalmente

        # 4. Botão de Exportação
        self.export_button = QPushButton("Exportar Tabela Atual para Excel")
        self.export_button.setObjectName("export_excel")
        self.export_button.clicked.connect(self.export_current_table)
        main_layout.addWidget(self.export_button)

        # Desabilitar botões se run.py não foi encontrado
        if not HAVE_RUN_SCRIPT:
            self.run_tables_button.setEnabled(False)
            self.run_text_button.setEnabled(False)
            self.run_consolidate_button.setEnabled(False)
            self.run_tables_button.setText("run.py não encontrado")
            self.log_browser.setHtml("<p style='color:red;'><b>ERRO CRÍTICO:</b> 'run.py' não foi importado. A funcionalidade de ETL está desabilitada.</p>")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a Pasta Raiz do PVRV")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(folder)
            self.log_browser.append(f"Pasta selecionada: {folder}")

    def run_worker(self, mode):
        if not self.selected_folder:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta primeiro.")
            return
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Aviso", "Uma tarefa já está em execução.")
            return

        self.log_browser.clear()
        self.set_buttons_enabled(False)

        self.thread = QThread()
        self.worker = Worker(self.selected_folder, mode)
        self.worker.moveToThread(self.thread)

        self.worker.progress.connect(self.update_log)
        self.worker.error.connect(self.on_worker_error)
        self.worker.table_ready.connect(self.add_table_tab)
        self.worker.finished.connect(self.cleanup_thread)
        self.thread.started.connect(self.worker.run)

        self.thread.start()

    def update_log(self, message):
        if HAVE_ANSI2HTML and ansi_converter:
            html_message = ansi_converter.convert(message, full=False)
            self.log_browser.append(html_message)
        else:
            self.log_browser.append(message)

    def on_worker_error(self, error_message):
        self.update_log(f"<p style='color:red;'><b>ERRO:</b> {error_message}</p>")
        QMessageBox.critical(self, "Erro na Execução", error_message)

    def add_table_tab(self, df_name, df_data):
        if not isinstance(df_data, pd.DataFrame) or df_data.empty:
            self.update_log(f"Aviso: Tabela '{df_name}' está vazia ou não é um DataFrame, não será exibida.")
            return

        table_view = QTableView()
        model = PandasModel(df_data)
        table_view.setModel(model)
        table_view.resizeColumnsToContents()
        
        # Guarda o modelo no widget para exportação
        table_view.setProperty("model_data", model) 

        self.tables_tab_widget.addTab(table_view, df_name)
        self.output_tabs.setCurrentWidget(self.tables_tab_widget) # Foca na aba de tabelas

    def export_current_table(self):
        if self.tables_tab_widget.count() == 0:
            QMessageBox.warning(self, "Aviso", "Nenhuma tabela para exportar.")
            return
            
        current_table_view = self.tables_tab_widget.currentWidget()
        if not current_table_view:
            QMessageBox.warning(self, "Aviso", "Nenhuma tabela selecionada.")
            return

        model = current_table_view.property("model_data")
        if not model or not isinstance(model, PandasModel):
            QMessageBox.warning(self, "Aviso", "Não foi possível encontrar os dados da tabela.")
            return
            
        filePath, _ = QFileDialog.getSaveFileName(self, "Salvar Tabela", "", "Excel Files (*.xlsx)")
        if filePath:
            try:
                model._data.to_excel(filePath, index=False)
                QMessageBox.information(self, "Sucesso", f"Tabela salva com sucesso em: {filePath}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível salvar o arquivo: {e}")

    def cleanup_thread(self):
        self.set_buttons_enabled(True)
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        self.worker = None
        self.thread = None

    def set_buttons_enabled(self, enabled):
        # Apenas reabilita se run.py existe
        is_run_available = HAVE_RUN_SCRIPT and enabled
        self.run_tables_button.setEnabled(is_run_available)
        self.run_text_button.setEnabled(is_run_available)
        self.run_consolidate_button.setEnabled(is_run_available)
        self.folder_button.setEnabled(enabled)

    # Não precisamos de closeEvent se este for um QWidget dentro de uma aba
    # A aba principal (MainView) cuidará do fechamento.

# --- Fim do Palkia_GUI.py ---
# ==============================================================================


# ==============================================================================
# 5. CLASSES DE WIDGETS (Funcionalidades / Abas)
# ==============================================================================

class PlaceholderWidget(QWidget):
    """Widget genérico para módulos em construção."""
    def __init__(self, module_name: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        label_title = QLabel(f"Módulo: {module_name}")
        label_title.setFont(QFont("Arial", 20, QFont.Bold))
        label_title.setAlignment(Qt.AlignCenter)
        
        label_status = QLabel("Em construção...")
        label_status.setFont(QFont("Arial", 14, QFont.Italic))
        label_status.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label_title)
        layout.addWidget(label_status)
        self.setLayout(layout)

# --- 5.1. Módulo Dashboard MUST (Exemplo Plotly) ---
class MustDashboardWidget(QWidget):
    """Widget para exibir o dashboard de MUST (exemplo com Plotly)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.webview = None

        if not HAVE_WEB_ENGINE:
            self.layout.addWidget(PlaceholderWidget("Dashboard MUST (PySide6-WebEngine não instalado)"))
            return

        if not (HAVE_PANDAS and HAVE_PLOTLY):
            self.layout.addWidget(PlaceholderWidget("Dashboard MUST (Pandas ou Plotly não instalados)"))
            return

        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)
        self.load_plot()
        
        # Conecta a mudança de tema para recarregar o gráfico
        try:
            # Tenta acessar o controller e conectar ao sinal
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'controller'):
                 main_window.controller.model.theme_changed.connect(self.on_theme_changed)
        except Exception as e:
            print(f"Aviso: Não foi possível conectar o dashboard à mudança de tema. {e}")

    def get_main_window(self) -> Optional[QMainWindow]:
        """Tenta encontrar a QMainWindow principal."""
        parent = self.parent()
        while parent:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None

    @Slot(str)
    def on_theme_changed(self, theme: str):
        """Recarrega o gráfico quando o tema muda."""
        print("Tema mudou, recarregando gráfico do dashboard...")
        self.load_plot()

    def load_plot(self):
        """Gera um gráfico Plotly e o carrega no QWebEngineView."""
        try:
            # 1. Criar dados de exemplo
            df = pd.DataFrame({
                "Empresa": ["CTEEP", "ISA", "TAESA", "Eletrosul"],
                "Aprovadas": [20, 35, 15, 28],
                "Com Ressalva": [5, 10, 8, 3],
                "Reprovadas": [2, 1, 4, 0]
            })
            df = df.melt(id_vars="Empresa", var_name="Status", value_name="Quantidade")

            # 2. Gerar o gráfico com Plotly
            fig = px.bar(df,
                         x="Empresa",
                         y="Quantidade",
                         color="Status",
                         title="Solicitações MUST por Empresa e Status (Exemplo)",
                         barmode="group",
                         color_discrete_map={
                             'Aprovadas': '#2ECC71',
                             'Com Ressalva': '#F39C12',
                             'Reprovadas': '#E74C3C'
                         }
            )
            
            # 3. Ajustar tema do gráfico (Dark/Light)
            current_theme = QApplication.instance().palette().color(QApplication.instance().palette().WindowText)
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color=current_theme.name() # Define a cor da fonte
            )

            # 4. Salvar como HTML temporário
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
                fig.write_html(f, full_html=True, include_plotlyjs='cdn')
                self.temp_html_file = f.name
            
            # 5. Carregar no QWebEngineView
            self.webview.load(QUrl.fromLocalFile(self.temp_html_file))

        except Exception as e:
            print(f"Erro ao gerar gráfico Plotly: {e}")
            logging.error(f"Erro ao gerar gráfico Plotly: {e}")
            self.layout.addWidget(QLabel(f"Erro ao gerar gráfico: {e}"))

    def __del__(self):
        """Garante que o arquivo HTML temporário seja excluído."""
        if hasattr(self, 'temp_html_file') and os.path.exists(self.temp_html_file):
            try:
                os.remove(self.temp_html_file)
            except Exception as e:
                print(f"Não foi possível remover o arquivo HTML temporário: {e}")

# --- 5.2. Módulo Gerar Relatório (HTML -> PDF) ---
class GerarRelatorioWidget(QWidget):
    """Widget para gerar relatórios PDF a partir de HTML usando WeasyPrint."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        if not HAVE_WEASYPRINT:
            self.layout.addWidget(PlaceholderWidget("Gerador de Relatórios (WeasyPrint não instalado)"))
            return

        self.layout.addWidget(QLabel("Gerador de Relatório (HTML para PDF)"))
        
        self.html_editor = QTextEdit()
        self.html_editor.setPlaceholderText("Escreva seu HTML aqui...")
        self.html_editor.setHtml(self.get_template_html())
        self.layout.addWidget(self.html_editor)
        
        self.generate_button = QPushButton("Gerar e Salvar PDF")
        self.generate_button.clicked.connect(self.generate_pdf)
        self.layout.addWidget(self.generate_button)
        
        self.setLayout(self.layout)

    def get_template_html(self) -> str:
        """Retorna um HTML de exemplo para o editor."""
        return """
<html>
<head>
    <style>
        body { font-family: 'Arial', sans-serif; line-height: 1.6; }
        h1 { color: #333; }
        .content { margin: 20px; }
        .highlight { color: #0078d4; font-weight: bold; }
        .approved { color: green; }
        .rejected { color: red; }
    </style>
</head>
<body>
    <h1>Relatório de Análise de Contingência</h1>
    <div class="content">
        <p>Este é um relatório de exemplo gerado automaticamente.</p>
        <p>A análise do ponto <span class="highlight">LT 500kV X-Y</span> foi
        <span class="approved">Aprovada com Ressalvas</span>.</p>
        <p>Observação: Necessário monitoramento na LT 230kV A-B.</p>
    </div>
</body>
</html>
"""

    @Slot()
    def generate_pdf(self):
        """Pega o HTML, pede um local para salvar e gera o PDF."""
        if not HAVE_WEASYPRINT:
            QMessageBox.critical(self, "Erro", "WeasyPrint não está instalado.")
            return

        html_content = self.html_editor.toHtml()
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório PDF", "", "Arquivos PDF (*.pdf)"
        )
        
        if not save_path:
            return # Usuário cancelou

        try:
            HTML(string=html_content).write_pdf(save_path)
            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em:\n{save_path}")
        except Exception as e:
            print(f"Erro ao gerar PDF com WeasyPrint: {e}")
            logging.error(f"Erro ao gerar PDF com WeasyPrint: {e}")
            QMessageBox.critical(self, "Erro na Geração", f"Falha ao gerar o PDF:\n{e}")

# --- 5.3. Outros Módulos (Placeholders) ---
class DashboardSPWidget(PlaceholderWidget):
    def __init__(self, parent=None):
        super().__init__("Dashboard Atividades SP", parent)

class DeckBuilderWidget(PlaceholderWidget):
    def __init__(self, parent=None):
        super().__init__("Deck Builder (AnaREDE)", parent)

class JuntaDeckWidget(PlaceholderWidget):
    def __init__(self, parent=None):
        super().__init__("Juntar Decks", parent)

class OrganizaArquivosWidget(PlaceholderWidget):
    def __init__(self, parent=None):
        super().__init__("Organizar Arquivos", parent)

class AgendamentoDEAPWidget(PlaceholderWidget):
    def __init__(self, parent=None):
        super().__init__("Agendamento Ótimo (DEAP)", parent)

class GestaoOBSWidget(PlaceholderWidget):
    def __init__(self, parent=None):
        super().__init__("Gestão Fora Ponta (OBS)", parent)


# ==============================================================================
# 6. GERENCIADOR DE DADOS (Exemplo)
# ==============================================================================

class DatabaseManager(QObject):
    """
    Classe para centralizar a lógica de banco de dados.
    (Parte do "Model" na arquitetura MVC)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sqlite_conn = None
        self.sql_server_conn = None
        
        self.setup_sqlite()
        self.setup_sql_server()

    def setup_sqlite(self):
        """Configura a conexão com o banco de dados local SQLite."""
        try:
            db_path = Path(__file__).parent / "gestao_ons.db"
            self.sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
            logging.info(f"Conexão SQLite estabelecida com: {db_path}")
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analises_must (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT DEFAULT CURRENT_TIMESTAMP,
                    ponto TEXT NOT NULL,
                    status TEXT,
                    observacao TEXT,
                    relatorio_path TEXT
                )
            """)
            self.sqlite_conn.commit()
        except Exception as e:
            print(f"Erro ao conectar/configurar SQLite: {e}")
            logging.error(f"Erro ao conectar/configurar SQLite: {e}")

    def setup_sql_server(self):
        """Configura a conexão com o SQL Server (via pyodbc)."""
        if not HAVE_PYODBC:
            logging.warning("Conexão SQL Server pulada (pyodbc não encontrado).")
            return
            
        try:
            # ATENÇÃO: Substituir pela sua string de conexão real
            conn_string = (
                r'DRIVER={ODBC Driver 17 for SQL Server};'
                r'SERVER=SEU_SERVIDOR_SQL;'
                r'DATABASE=SEU_BANCO_DE_DADOS;'
                r'Trusted_Connection=yes;' # Recomendado
            )
            # self.sql_server_conn = pyodbc.connect(conn_string)
            # logging.info("Conexão SQL Server estabelecida (simulada).")
            logging.info("Tentativa de conexão SQL Server (pyodbc) pronta. Descomente a linha acima com sua string.")
        except Exception as e:
            print(f"Erro ao conectar com SQL Server via pyodbc: {e}")
            logging.error(f"Erro ao conectar com SQL Server via pyodbc: {e}")
            print("Verifique sua string de conexão e se os drivers ODBC estão instalados.")


# ==============================================================================
# 7. ARQUITETURA MVC (Model, View, Controller)
# ==============================================================================

# --- 7.1. MODEL ---
class AppModel(QObject):
    """
    Armazena o estado da aplicação.
    - theme: 'dark' ou 'light'
    - pages: lista de dicionários descrevendo as abas abertas
    """
    theme_changed = Signal(str)
    pages_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._theme = "dark" # Inicia com o tema dark (seu estilo padrão)
        self._pages: List[Dict[str, Any]] = []

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str):
        self._theme = value
        self.theme_changed.emit(value) # Emite o sinal

    def add_page(self, key: str, title: str, data: Any = None) -> bool:
        """Adiciona uma nova aba se ela já não estiver aberta."""
        if any(p.get("key") == key for p in self._pages):
            logging.warning(f"Página com chave '{key}' já está aberta.")
            return False
            
        page_data = {"key": key, "title": title, "data": data}
        self._pages.append(page_data)
        self.pages_changed.emit()
        return True

    def remove_page(self, index: int):
        """Remove uma página pelo seu índice."""
        if 0 <= index < len(self._pages):
            del self._pages[index]
            self.pages_changed.emit()

    def get_pages(self) -> List[Dict[str, Any]]:
        return self._pages
    
    def get_page_index_by_key(self, key: str) -> int:
        """Encontra o índice de uma página pela sua chave."""
        for i, page in enumerate(self._pages):
            if page.get("key") == key:
                return i
        return -1


# --- 7.2. VIEW ---
class MainView(QMainWindow):
    """
    A Janela Principal (View).
    Constrói a interface (Toolbar, Menu, Abas) mas não contém lógica.
    """
    tree_item_activated = Signal(str) # Emite a 'key' do item
    close_tab_requested = Signal(int)
    toggle_theme_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Controle e Gestão - PLC - ONS 2025")
        self.resize(1400, 800)
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.toolbar = QToolBar("Barra de Ferramentas")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.action_toggle_theme = self.toolbar.addAction("Trocar Tema (Dark/Light)")
        self.action_toggle_theme.triggered.connect(self.toggle_theme_requested)

        self.tree_menu = QTreeWidget()
        self.tree_menu.setHeaderHidden(True)
        self.tree_menu.setMinimumWidth(250)
        self.tree_menu.setMaximumWidth(300)
        main_layout.addWidget(self.tree_menu)
        self.populate_tree()
        self.tree_menu.itemActivated.connect(self.on_tree_item_activated)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab_requested)
        main_layout.addWidget(self.tabs)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.insertWidget(1, line)

    def populate_tree(self):
        """Preenche o menu em árvore com os módulos da aplicação."""
        self.tree_menu.clear()

        # Categoria 1: Dashboards
        cat_dash = QTreeWidgetItem(self.tree_menu, ["Dashboards"])
        cat_dash.setFont(0, QFont("Arial", 11, QFont.Bold))
        
        item_dash_must = QTreeWidgetItem(cat_dash, ["Dashboard MUST"])
        item_dash_must.setData(1, 0, "dash_must") # key = 'dash_must'
        
        item_dash_sp = QTreeWidgetItem(cat_dash, ["Dashboard Atividades SP"])
        item_dash_sp.setData(1, 0, "dash_sp") # key = 'dash_sp'

        # Categoria 2: Ferramentas
        cat_tools = QTreeWidgetItem(self.tree_menu, ["Ferramentas"])
        cat_tools.setFont(0, QFont("Arial", 11, QFont.Bold))

        item_palkia = QTreeWidgetItem(cat_tools, ["Palkia ETL (PVRV)"])
        item_palkia.setData(1, 0, "palkia") # key = 'palkia'

        item_deck_builder = QTreeWidgetItem(cat_tools, ["Deck Builder (AnaREDE)"])
        item_deck_builder.setData(1, 0, "deck_builder") # key = 'deck_builder'
        
        item_junta_deck = QTreeWidgetItem(cat_tools, ["Juntar Decks"])
        item_junta_deck.setData(1, 0, "junta_deck") # key = 'junta_deck'

        item_organiza = QTreeWidgetItem(cat_tools, ["Organizar Arquivos"])
        item_organiza.setData(1, 0, "organiza_arq") # key = 'organiza_arq'

        # Categoria 3: Análise
        cat_analise = QTreeWidgetItem(self.tree_menu, ["Análise de Contingência"])
        cat_analise.setFont(0, QFont("Arial", 11, QFont.Bold))

        item_agendamento = QTreeWidgetItem(cat_analise, ["Agendamento Ótimo (DEAP)"])
        item_agendamento.setData(1, 0, "agendamento_deap") # key = 'agendamento_deap'

        item_gestao_obs = QTreeWidgetItem(cat_analise, ["Gestão Fora Ponta (OBS)"])
        item_gestao_obs.setData(1, 0, "gestao_obs") # key = 'gestao_obs'

        # Categoria 4: Relatórios
        cat_relatorios = QTreeWidgetItem(self.tree_menu, ["Relatórios"])
        cat_relatorios.setFont(0, QFont("Arial", 11, QFont.Bold))
        
        item_gerar_relatorio = QTreeWidgetItem(cat_relatorios, ["Gerar Relatório PDF"])
        item_gerar_relatorio.setData(1, 0, "gerar_relatorio") # key = 'gerar_relatorio'

        self.tree_menu.expandAll()

    @Slot(QTreeWidgetItem, int)
    def on_tree_item_activated(self, item: QTreeWidgetItem, column: int):
        """Pega a 'key' do item e a emite no sinal."""
        item_key = item.data(1, 0)
        if item_key:
            self.tree_item_activated.emit(item_key)

    def set_theme(self, theme: str):
        """Aplica o stylesheet QSS (Dark ou Light)."""
        if theme == 'dark':
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def add_tab_with_widget(self, widget: QWidget, title: str) -> int:
        """Adiciona um widget a uma nova aba."""
        return self.tabs.addTab(widget, title)

    def set_current_tab_by_index(self, index: int):
        """Muda o foco para a aba no índice."""
        self.tabs.setCurrentIndex(index)


# --- 7.3. CONTROLLER ---
class AppController(QObject):
    """
    O "Cérebro" (Controller).
    Conecta o Model e a View, aplicando a lógica de negócio.
    """
    def __init__(self, model: AppModel, view: MainView):
        super().__init__()
        self.model = model
        self.view = view
        # Passa a view como 'parent' do controller
        # para que os widgets filhos (como o dashboard) possam encontrá-la.
        self.view.controller = self 
        
        self.db_manager = DatabaseManager(self) # Gerenciador de BD
        self.open_tab_widgets: Dict[int, QWidget] = {}

        self.connect_signals()
        
        # Sincronizar estado inicial
        self.on_theme_changed(self.model.theme)
        self.sync_view_with_model()

    def connect_signals(self):
        """Conecta todos os sinais."""
        self.model.theme_changed.connect(self.on_theme_changed)
        self.model.pages_changed.connect(self.sync_view_with_model)
        
        self.view.toggle_theme_requested.connect(self.toggle_theme)
        self.view.tree_item_activated.connect(self.handle_tree_item_activated)
        self.view.close_tab_requested.connect(self.handle_close_tab)

    @Slot()
    def toggle_theme(self):
        """Lógica para trocar o tema."""
        new_theme = "light" if self.model.theme == "dark" else "dark"
        self.model.theme = new_theme

    @Slot(str)
    def on_theme_changed(self, theme: str):
        """Slot que reage à mudança de tema no modelo."""
        self.view.set_theme(theme)
        logging.info(f"Tema alterado para: {theme}")

    @Slot(int)
    def handle_close_tab(self, index: int):
        """Lógica para fechar uma aba."""
        self.model.remove_page(index)
        # O modelo emitirá 'pages_changed', que chamará 'sync_view_with_model'

    @Slot(str)
    def handle_tree_item_activated(self, key: str):
        """Lógica para abrir uma aba ao clicar na árvore."""
        item = self.find_tree_item_by_key(key)
        title = item.text(0) if item else key.replace("_", " ").title()

        existing_index = self.model.get_page_index_by_key(key)
        if existing_index != -1:
            self.view.set_current_tab_by_index(existing_index)
            return

        self.model.add_page(key=key, title=title)
        # O modelo emitirá 'pages_changed', que chamará 'sync_view_with_model'
        # O 'sync_view_with_model' focará na nova aba.

    def find_tree_item_by_key(self, key: str) -> Optional[QTreeWidgetItem]:
        """Busca um item na árvore pela sua 'key'."""
        iterator = QTreeWidgetItemIterator(self.view.tree_menu)
        while iterator.value():
            item = iterator.value()
            if item.data(1, 0) == key:
                return item
            iterator += 1
        return None

    def create_widget_for_page(self, page_data: Dict[str, Any]) -> QWidget:
        """
        Factory: Cria o QWidget correto com base na 'key' da página.
        """
        key = page_data.get("key")
        
        # Mapeamento de 'key' para a classe do Widget
        # Aqui conectamos as classes que definimos acima!
        widget_map = {
            "palkia": PalkiaWindowGUI,           # <-- Seu widget real integrado
            "dash_must": MustDashboardWidget,       # <-- Dashboard Plotly
            "gerar_relatorio": GerarRelatorioWidget,  # <-- Gerador de PDF
            "dash_sp": DashboardSPWidget,           # <-- Placeholder
            "deck_builder": DeckBuilderWidget,      # <-- Placeholder
            "junta_deck": JuntaDeckWidget,          # <-- Placeholder
            "organiza_arq": OrganizaArquivosWidget, # <-- Placeholder
            "agendamento_deap": AgendamentoDEAPWidget,# <-- Placeholder
            "gestao_obs": GestaoOBSWidget,        # <-- Placeholder
        }

        WidgetClass = widget_map.get(key)
        
        if WidgetClass:
            return WidgetClass()
        else:
            # Fallback para qualquer 'key' não mapeada
            title = page_data.get("title", key)
            return PlaceholderWidget(title)

    @Slot()
    def sync_view_with_model(self):
        """
        Atualiza o QTabWidget (View) para corresponder ao self.model._pages (Model).
        """
        current_model_key = None
        current_view_index = self.view.tabs.currentIndex()
        if 0 <= current_view_index < len(self.model.get_pages()):
             current_model_key = self.model.get_pages()[current_view_index].get("key")

        self.view.tabs.clear()
        
        # Limpa o cache de widgets (pode ser otimizado no futuro)
        for widget in self.open_tab_widgets.values():
             widget.deleteLater() # Garante limpeza de memória
        self.open_tab_widgets.clear() 

        # Recria as abas a partir do modelo
        for index, page_data in enumerate(self.model.get_pages()):
            title = page_data.get("title", "Sem Título")
            widget = self.create_widget_for_page(page_data)
            self.open_tab_widgets[index] = widget
            self.view.add_tab_with_widget(widget, title)

        # Restaura o foco
        if current_model_key:
            new_index = self.model.get_page_index_by_key(current_model_key)
            if new_index != -1:
                self.view.set_current_tab_by_index(new_index)
            elif self.view.tabs.count() > 0:
                 self.view.set_current_tab_by_index(self.view.tabs.count() - 1)
        elif self.view.tabs.count() > 0:
            # Foca na última aba (a nova)
            self.view.set_current_tab_by_index(self.view.tabs.count() - 1)


# ==============================================================================
# 8. PONTO DE ENTRADA DA APLICAÇÃO (main)
# ==============================================================================

def setup_logging():
    """Configura o sistema de logs para salvar em arquivo e mostrar no console."""
    log_file = Path(__file__).parent / "app_gestao.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Aplicação iniciada. Sistema de logs configurado.")

def main():
    """Função principal que inicia a aplicação."""
    setup_logging()
    app = QApplication(sys.argv)
    
    # Configurações para QWebEngine (se disponível)
    if HAVE_WEB_ENGINE:
        # Habilita dev tools (F12) - útil para depurar Plotly
        os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9223"
        logging.info("WebEngine DevTools disponível em http://localhost:9223")

    model = AppModel()
    view = MainView()
    controller = AppController(model=model, view=view)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()