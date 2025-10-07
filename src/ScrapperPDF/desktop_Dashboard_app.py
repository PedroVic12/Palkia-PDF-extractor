import sys
import sqlite3
import pyodbc
import webbrowser
import os
import re
from pathlib import Path
from datetime import datetime
from io import StringIO
import tempfile
import logging

from PySide6.QtCore import (
    Qt, QUrl, QThread, QObject, Signal, QAbstractTableModel, Property,
    QPropertyAnimation, QEasingCurve, QSize
)
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QFrame, QDialog, QTextBrowser, QTabWidget,
    QProgressBar, QStackedWidget, QFileDialog, QMessageBox, QTextEdit, QGroupBox,
    QTableView, QListWidget, QAbstractButton, QSizePolicy, QListWidgetItem
)

try:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from PySide6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("Dependências (pandas, plotly, PySide6-WebEngine) não encontradas.")
    pd = px = go = QWebEngineView = None

try:
    from ansi2html import Ansi2HTMLConverter
    ansi_converter = Ansi2HTMLConverter(dark_bg=True, scheme="xterm")
except ImportError:
    ansi_converter = None

try:
    import run as run_script
except ImportError:
    run_script = None
    print("AVISO: Módulo 'run.py' não encontrado.")

# ==============================================================================
# ESTILOS (QSS)
# ==============================================================================
# Os estilos agora são definidos aqui para facilitar a troca de temas.
DARK_STYLE = """
    QWidget {
        background-color: #202020; color: #FFFFFF; font-family: 'Segoe UI'; font-size: 14px;
    }
    QMainWindow { background-color: #2D2D2D; }
    QFrame#navPanel { background-color: #2D2D2D; border-right: 1px solid #404040; }
    QFrame#container, QFrame#kpiCard { background-color: #1F2937; border-radius: 8px; }
    QListWidget { border: none; padding-top: 10px; }
    QListWidget::item { padding: 12px 20px; border-radius: 5px; }
    QListWidget::item:hover { background-color: #353535; }
    QListWidget::item:selected { background-color: #0078D4; color: #FFFFFF; }
    QLabel#headerTitle { font-size: 28px; font-weight: 600; padding: 20px; }
    QLabel#sectionTitle { font-size: 18px; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }
    QComboBox { background-color: #3C3C3C; border: 1px solid #505050; border-radius: 4px; padding: 5px 10px; }
    QPushButton#filterButton { background-color: #EA580C; color: white; text-align: center; }
    QPushButton#clearButton { background-color: transparent; border: 1px solid #6B7280; text-align: center; }
"""

LIGHT_STYLE = """
    QWidget {
        background-color: #F3F3F3; color: #000000; font-family: 'Segoe UI'; font-size: 14px;
    }
    QMainWindow { background-color: #E0E0E0; }
    QFrame#navPanel { background-color: #E0E0E0; border-right: 1px solid #C0C0C0; }
    QFrame#container, QFrame#kpiCard { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }
    QListWidget { border: none; padding-top: 10px; }
    QListWidget::item { padding: 12px 20px; border-radius: 5px; }
    QListWidget::item:hover { background-color: #DCDCDC; }
    QListWidget::item:selected { background-color: #0078D4; color: #FFFFFF; }
    QLabel#headerTitle { font-size: 28px; font-weight: 600; padding: 20px; }
    QLabel#sectionTitle { font-size: 18px; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }
    QComboBox { background-color: #FFFFFF; border: 1px solid #C0C0C0; border-radius: 4px; padding: 5px 10px; }
    QPushButton#filterButton { background-color: #EA580C; color: white; text-align: center; }
    QPushButton#clearButton { background-color: #FFFFFF; border: 1px solid #C0C0C0; text-align: center; }
"""
# ==============================================================================
# MODELOS DE DADOS (DATABASE)
# ==============================================================================
class DashboardDB:
    # ... (código do DashboardDB, sem alterações)
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Arquivo de banco de dados não encontrado: {self.db_path}")

        self.db_type = 'access' if self.db_path.suffix.lower() == '.accdb' else 'sqlite'
        
        if self.db_type == 'sqlite':
            self.tbl_empresas, self.tbl_anotacao, self.tbl_valores = 'empresas', 'anotacao', 'valores_must'
        else:
            self.tbl_empresas, self.tbl_anotacao, self.tbl_valores = 'tb_empresas', 'tb_anotacao', 'tb_valores_must'

        if self.db_type == 'sqlite':
            self._ensure_approval_columns_exist_sqlite()

        self.company_links = {
            'SUL SUDESTE': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EbWWq1r7MnxPvOejycbr82cB5a_rN_PCsDMDjp9r3bF3Ng?e=C7dxKN',
            'ELETROPAULO': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EXzdo_ClziVDrnOHTiGzoysBdqgci92tpuKYN2xKIjPQvw?e=kzrFho',
        }

    def _get_connection(self):
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            conn_str = (r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" fr"DBQ={self.db_path};")
            return pyodbc.connect(conn_str)

    def _execute_query(self, query, params=(), fetch_one=False):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    if fetch_one:
                        result = cursor.fetchone()
                        return dict(zip(columns, result)) if result else None
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                return []
        except (sqlite3.Error, pyodbc.Error) as e:
            logging.error(f"Erro de banco de dados (leitura): {e}")
            return [] if not fetch_one else None

    def _execute_write_query(self, query, params=()):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
            return True
        except (sqlite3.Error, pyodbc.Error) as e:
            logging.error(f"Erro de banco de dados (escrita): {e}")
            return False

    def _ensure_approval_columns_exist_sqlite(self):
        try:
            table_info = self._execute_query(f"PRAGMA table_info({self.tbl_anotacao})")
            column_names = [col['name'] for col in table_info]
            if 'aprovado_por' not in column_names:
                self._execute_write_query(f"ALTER TABLE {self.tbl_anotacao} ADD COLUMN aprovado_por TEXT;")
            if 'data_aprovacao' not in column_names:
                self._execute_write_query(f"ALTER TABLE {self.tbl_anotacao} ADD COLUMN data_aprovacao TEXT;")
        except Exception as e:
            logging.error(f"Erro ao verificar tabela '{self.tbl_anotacao}': {e}")
            
    def get_kpi_summary(self):
        query_companies = f"SELECT COUNT(*) as count FROM {self.tbl_empresas};"
        query_points = f"SELECT COUNT(*) as count FROM {self.tbl_anotacao};"
        query_remarks = f"SELECT COUNT(*) as count FROM {self.tbl_anotacao} WHERE anotacao_geral IS NOT NULL AND anotacao_geral <> '' AND anotacao_geral <> 'nan';"
        try:
            total_companies = self._execute_query(query_companies, fetch_one=True)['count']
            total_points = self._execute_query(query_points, fetch_one=True)['count']
            points_with_remarks = self._execute_query(query_remarks, fetch_one=True)['count']
            percentage = (points_with_remarks / total_points * 100) if total_points > 0 else 0
            return {'unique_companies': total_companies, 'total_points': total_points, 'points_with_remarks': points_with_remarks, 'percentage_with_remarks': f"{percentage:.1f}%"}
        except (TypeError, KeyError, ZeroDivisionError) as e:
            logging.error(f"Erro ao calcular KPIs: {e}")
            return {'unique_companies': 0, 'total_points': 0, 'points_with_remarks': 0, 'percentage_with_remarks': '0.0%'}

    def get_company_analysis(self): return self._execute_query(f"SELECT e.nome_empresa, COUNT(a.id_conexao) as total, SUM(IIF(a.anotacao_geral IS NOT NULL AND a.anotacao_geral <> '' AND a.anotacao_geral <> 'nan', 1, 0)) as with_remarks FROM {self.tbl_empresas} AS e INNER JOIN {self.tbl_anotacao} AS a ON e.id_empresa = a.id_empresa GROUP BY e.nome_empresa ORDER BY e.nome_empresa;")
    def get_yearly_must_stats(self): return self._execute_query(f"SELECT ano, periodo, SUM(valor) as total_valor FROM {self.tbl_valores} GROUP BY ano, periodo ORDER BY ano, periodo;")
    def get_unique_companies(self): return [row['nome_empresa'] for row in self._execute_query(f"SELECT nome_empresa FROM {self.tbl_empresas} ORDER BY nome_empresa;")]
    def get_unique_tensions(self): return [str(row['tensao_kv']) for row in self._execute_query(f"SELECT DISTINCT tensao_kv FROM {self.tbl_anotacao} WHERE tensao_kv IS NOT NULL ORDER BY tensao_kv;")]
    def get_must_history_for_point(self, cod_ons): return self._execute_query(f"SELECT vm.ano, vm.periodo, vm.valor FROM {self.tbl_valores} AS vm INNER JOIN {self.tbl_anotacao} AS a ON vm.id_conexao = a.id_conexao WHERE a.cod_ons = ? ORDER BY vm.ano, vm.periodo;", (cod_ons,))
    def approve_point(self, cod_ons, approver_name): return self._execute_write_query(f"UPDATE {self.tbl_anotacao} SET aprovado_por = ?, data_aprovacao = ? WHERE cod_ons = ?;", (approver_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cod_ons))
    def get_data_for_charts(self): return {"points_per_company": self._execute_query(f"SELECT e.nome_empresa, COUNT(a.id_conexao) as count FROM {self.tbl_empresas} AS e INNER JOIN {self.tbl_anotacao} AS a ON e.id_empresa = a.id_empresa GROUP BY e.nome_empresa"), "remarks_summary": self._execute_query(f"SELECT SUM(IIF(anotacao_geral IS NOT NULL AND anotacao_geral <> '' AND anotacao_geral <> 'nan', 1, 0)) as with_remarks, COUNT(id_conexao) as total FROM {self.tbl_anotacao}", fetch_one=True), "yearly_sum": self._execute_query(f"SELECT ano, SUM(valor) as total_valor FROM {self.tbl_valores} GROUP BY ano ORDER BY ano")}
    def get_all_connection_points(self, filters=None):
        query = f"SELECT emp.nome_empresa, a.cod_ons, a.tensao_kv, a.anotacao_geral, a.aprovado_por, a.data_aprovacao FROM {self.tbl_empresas} AS emp INNER JOIN {self.tbl_anotacao} AS a ON emp.id_empresa = a.id_empresa"
        conditions, params = [], []
        # ... (lógica de filtro)
        if conditions: query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY emp.nome_empresa, a.cod_ons;"
        #...
        return self._execute_query(query, tuple(params))

class SettingsModel(QObject):
    DB_FILE = "settings.db"
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._theme = "dark"
        self._db_conn = self._create_db_connection()
        self._load_from_db()

    def _create_db_connection(self):
        try:
            conn = sqlite3.connect(self.DB_FILE)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            conn.commit()
            return conn
        except sqlite3.Error as e:
            logging.error(f"Erro ao conectar ao BD de configurações: {e}")
            return None

    def _load_from_db(self):
        if not self._db_conn: return
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            settings = dict(cursor.fetchall())
            self.theme = settings.get("theme", self._theme)
        except sqlite3.Error as e:
            logging.error(f"Erro ao carregar configurações: {e}")

    def _save_to_db(self, key, value):
        if not self._db_conn: return
        try:
            cursor = self._db_conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            self._db_conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao salvar '{key}': {e}")

    @property
    def theme(self): return self._theme

    @theme.setter
    def theme(self, value):
        self._theme = value; self._save_to_db("theme", value); self.theme_changed.emit(value)

class PandasModel(QAbstractTableModel):
    def __init__(self, data): super().__init__(); self._data = data
    def rowCount(self, parent=None): return self._data.shape[0]
    def columnCount(self, parent=None): return self._data.shape[1]
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole: return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal: return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical: return str(self._data.index[section])
        return None

class Worker(QObject):
    progress=Signal(str);finished=Signal();error=Signal(str)
    def __init__(self,t, *a, **k):super().__init__();self.t=t;self.a=a;self.k=k
    def run(self):
        so=sys.stdout;r=sys.stdout=StringIO()
        try:self.progress.emit(f"▶️ {self.t.__name__}");self.t(*self.a,**self.k);sys.stdout=so;o=r.getvalue();[self.progress.emit(l) for l in o.splitlines()];self.finished.emit()
        except Exception as e:sys.stdout=so;o=r.getvalue();[self.progress.emit(l) for l in o.splitlines()];import traceback;self.error.emit(f"❌ {e}\n{traceback.format_exc()}")

# ==============================================================================
# VIEWS (Telas da Aplicação)
# ==============================================================================
class DetailsDialog(QDialog):
    def __init__(self, annotation, history, parent=None):
        super().__init__(parent);self.setWindowTitle("Detalhes");self.setMinimumSize(700,500);self.setStyleSheet(STYLESHEET);l=QVBoxLayout(self);t=QTabWidget();r=QWidget();rl=QVBoxLayout(r);tv=QTextBrowser();tv.setPlainText(annotation or "Nenhuma.");rl.addWidget(tv);h=QWidget();hl=QVBoxLayout(h);ht=QTableWidget();ht.setColumnCount(3);ht.setHorizontalHeaderLabels(["Ano","Período","Valor"]);ht.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);ht.setRowCount(len(history));[ht.setItem(i,0,QTableWidgetItem(str(row['ano']))) or ht.setItem(i,1,QTableWidgetItem(str(row['periodo']))) or ht.setItem(i,2,QTableWidgetItem(f"{row.get('valor',0):.2f}")) for i,row in enumerate(history)];hl.addWidget(ht);t.addTab(r,"Ressalva");t.addTab(h,"Histórico");cb=QPushButton("Fechar");cb.clicked.connect(self.accept);l.addWidget(t);l.addWidget(cb,0,Qt.AlignmentFlag.AlignRight)

class ApprovalDialog(QDialog):
    def __init__(self, cod_ons, parent=None):
        super().__init__(parent);self.setWindowTitle("Aprovar");self.setStyleSheet(STYLESHEET);self.setMinimumWidth(400);self.approver_name="";l=QVBoxLayout(self);l.addWidget(QLabel(f"<b>Ponto:</b> {cod_ons}"));l.addWidget(QLabel("Seu nome:"))
        self.name_input=QLineEdit();l.addWidget(self.name_input);bl=QHBoxLayout();self.cb=QPushButton("Confirmar");self.cb.clicked.connect(self.accept);self.cancelb=QPushButton("Cancelar");self.cancelb.clicked.connect(self.reject);bl.addWidget(self.cb);bl.addWidget(self.cancelb);l.addLayout(bl)
    def accept(self):
        if self.name_input.text().strip():self.approver_name=self.name_input.text().strip();super().accept()
        else:self.name_input.setStyleSheet("border: 1px solid red;")

class CompanyCard(QFrame):
    def __init__(self, name, stats, parent=None):
        super().__init__(parent);self.setObjectName("kpiCard");r,t=stats.get('with_remarks',0),stats.get('total',0);p=(r/t*100)if t>0 else 0;l=QVBoxLayout(self);nl=QLabel(name);nl.setStyleSheet("font-weight:bold;");sl=QLabel(f"Ressalvas: {r}/{t}");sl.setObjectName("kpiTitle");self.pb=QProgressBar();self.pb.setValue(int(p));self.pb.setFormat(f"{p:.1f}%");l.addWidget(nl);l.addWidget(sl);l.addWidget(self.pb)

class PDFExtractionWidget(QWidget):
    # ... (código completo e restaurado da tela de extração)
    def __init__(self, parent=None): super().__init__(parent); self.input_folder = None; self.current_task_info = {}; self.thread = None; self.worker = None; self._setup_ui()
    def _setup_ui(self):
        main_layout=QVBoxLayout(self);main_layout.setContentsMargins(20,20,20,20);main_layout.setSpacing(20);self.setStyleSheet(APP_STYLES);title=QLabel("Extração de Dados de PDF MUST");title.setObjectName("headerTitle");subtitle=QLabel("Automatize a extração de tabelas e anotações");subtitle.setObjectName("headerSubtitle");main_layout.addWidget(title);main_layout.addWidget(subtitle);config_group=QGroupBox("Configuração");config_layout=QVBoxLayout(config_group);folder_layout=QHBoxLayout();self.folder_label=QLabel("Pasta: (Nenhuma)");self.folder_button=QPushButton("Selecionar");self.folder_button.clicked.connect(self._select_folder);folder_layout.addWidget(self.folder_label,1);folder_layout.addWidget(self.folder_button);config_layout.addLayout(folder_layout);intervals_label=QLabel("Intervalos de Páginas:");self.intervals_input=QLineEdit();self.intervals_input.setPlaceholderText('Ex: "8-16", "8-24"');config_layout.addWidget(intervals_label);config_layout.addWidget(self.intervals_input);main_layout.addWidget(config_group);actions_group=QGroupBox("Ações");actions_layout=QHBoxLayout(actions_group);self.run_tables_button=QPushButton("1) Extrair Tabelas");self.run_text_button=QPushButton("2) Extrair Anotações");self.run_consolidate_button=QPushButton("3) Consolidar");self.run_tables_button.clicked.connect(lambda:self._run_task("extract_tables"));self.run_text_button.clicked.connect(lambda:self._run_task("extract_text"));self.run_consolidate_button.clicked.connect(lambda:self._run_task("consolidate"));actions_layout.addWidget(self.run_tables_button);actions_layout.addWidget(self.run_text_button);actions_layout.addWidget(self.run_consolidate_button);main_layout.addWidget(actions_group);results_tabs=QTabWidget();log_widget=QWidget();log_layout=QVBoxLayout(log_widget);self.log_output=QTextEdit();self.log_output.setReadOnly(True);log_layout.addWidget(self.log_output);results_tabs.addTab(log_widget,"Log");table_widget=QWidget();table_layout=QVBoxLayout(table_widget);self.table_view=QTableView();self.export_button=QPushButton("Exportar");self.export_button.clicked.connect(self._export_table);self.export_button.setEnabled(False);table_layout.addWidget(self.table_view);table_layout.addWidget(self.export_button);results_tabs.addTab(table_widget,"Resultado");main_layout.addWidget(results_tabs);self.results_tabs=results_tabs
    def _select_folder(self): folder=QFileDialog.getExistingDirectory(self,"Selecione a pasta");
        if folder:self.input_folder=folder;self.folder_label.setText(f"Pasta: ...{os.path.basename(folder)}");self._append_log(f"Pasta selecionada: {folder}")
    def _run_task(self,task_name):
        if not run_script:QMessageBox.warning(self,"Módulo Ausente","'run.py' não disponível.");return
        if not self.input_folder:QMessageBox.warning(self,"Aviso","Selecione uma pasta.");return
        intervals=self.intervals_input.text();
        if task_name=="extract_tables" and not intervals:QMessageBox.warning(self,"Aviso","Forneça os intervalos.");return
        self.log_output.clear();self._set_buttons_enabled(False);self.table_view.setModel(None);self.export_button.setEnabled(False);self.current_task_info={"name":task_name,"input_folder":self.input_folder};run_script.input_folder=self.input_folder
        if task_name=="extract_tables":target_function=run_script.run_extract_PDF_tables;args=([i.strip() for i in intervals.split(',')], "folder")
        elif task_name=="extract_text":target_function=run_script.extract_text_from_must_tables;args=("folder",)
        elif task_name=="consolidate":target_function=run_script.consolidate_and_merge_results;args=()
        else:self._set_buttons_enabled(True);return
        self.thread=QThread();self.worker=Worker(target_function,*args);self.worker.moveToThread(self.thread);self.thread.started.connect(self.worker.run);self.worker.finished.connect(self._on_task_finished);self.worker.progress.connect(self._append_log);self.worker.error.connect(self._on_task_error);self.thread.start()
    def _append_log(self,text):
        if ansi_converter:self.log_output.append(ansi_converter.convert(text,full=False))
        else:self.log_output.append(re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])','',text))
    def _on_task_finished(self):self._append_log("\nTarefa concluída.");self._display_results();self._cleanup_thread()
    def _on_task_error(self,msg):self._append_log(f"\n{msg}");self._cleanup_thread()
    def _display_results(self): pass
    def _export_table(self): pass
    def _cleanup_thread(self):self._set_buttons_enabled(True);
        if self.thread:self.thread.quit();self.thread.wait();self.worker=None;self.thread=None
    def _set_buttons_enabled(self,enabled):self.run_tables_button.setEnabled(enabled);self.run_text_button.setEnabled(enabled);self.run_consolidate_button.setEnabled(enabled);self.folder_button.setEnabled(enabled)

class DashboardMainWidget(QWidget):
    filters_applied=Signal(dict);approve_requested=Signal(int);details_requested=Signal(int);link_clicked=Signal(int,int)
    def __init__(self,parent=None):super().__init__(parent);self._setup_ui()
    def _setup_ui(self):
        self.main_layout=QVBoxLayout(self);self.main_layout.setContentsMargins(20,20,20,20);self.main_layout.setSpacing(20)
        self._create_header();self.main_layout.addWidget(self._create_kpi_container());self.main_layout.addWidget(self._create_company_analysis_container())
        self.main_layout.addWidget(self._create_yearly_stats_container());self.main_layout.addWidget(self._create_filters_container());self.main_layout.addWidget(self._create_details_table_container());self.main_layout.addStretch()
    def _create_header(self):h=QVBoxLayout();t=QLabel("Dashboard de Análise");t.setObjectName("headerTitle");s=QLabel("Visão geral das solicitações");s.setObjectName("headerSubtitle");h.addWidget(t);h.addWidget(s);self.main_layout.addLayout(h)
    def _create_kpi_container(self):
        c=QFrame();c.setObjectName("container");l=QVBoxLayout(c);l.addWidget(QLabel("Visão Geral",objectName="sectionTitle"))
        self.kpi_layout=QHBoxLayout();self.kpi_cards={"uc":self._create_kpi_card("Empresas","0"),"tp":self._create_kpi_card("Pontos","0"),"pr":self._create_kpi_card("Com Ressalvas","0"),"ppr":self._create_kpi_card("% Ressalvas","0.0%")};[self.kpi_layout.addWidget(card)for card in self.kpi_cards.values()];l.addLayout(self.kpi_layout);return c
    def _create_kpi_card(self,t,v):c=QFrame();c.setObjectName("kpiCard");l=QVBoxLayout(c);tl=QLabel(t);vl=QLabel(v);tl.setObjectName("kpiTitle");vl.setObjectName("kpiValue");l.addWidget(tl);l.addWidget(vl);return c
    def _create_company_analysis_container(self):c=QFrame();c.setObjectName("container");l=QVBoxLayout(c);l.addWidget(QLabel("Análise por Empresa",objectName="sectionTitle"));self.company_analysis_layout=QGridLayout();l.addLayout(self.company_analysis_layout);return c
    def _create_yearly_stats_container(self):c=QFrame();c.setObjectName("container");l=QVBoxLayout(c);l.addWidget(QLabel("Estatísticas Anuais",objectName="sectionTitle"));self.yearly_stats_layout=QGridLayout();l.addLayout(self.yearly_stats_layout);return c
    def _create_filters_container(self):
        c=QFrame();c.setObjectName("container");l=QVBoxLayout(c);l.addWidget(QLabel("Filtros",objectName="sectionTitle"));g=QGridLayout();g.addWidget(QLabel("Empresa"),0,0);g.addWidget(QLabel("Pesquisar"),0,1);g.addWidget(QLabel("Ano"),0,2);g.addWidget(QLabel("Tensão"),0,3);g.addWidget(QLabel("Status"),0,4)
        self.company_combo=QComboBox();self.search_input=QLineEdit();self.year_combo=QComboBox();self.tension_combo=QComboBox();self.status_combo=QComboBox();g.addWidget(self.company_combo,1,0);g.addWidget(self.search_input,1,1);g.addWidget(self.year_combo,1,2);g.addWidget(self.tension_combo,1,3);g.addWidget(self.status_combo,1,4)
        b=QHBoxLayout();b.addStretch();self.clear_button=QPushButton("Limpar");self.clear_button.clicked.connect(self._clear_filters);self.filter_button=QPushButton("Filtrar");self.filter_button.clicked.connect(self._apply_filters);b.addWidget(self.clear_button);b.addWidget(self.filter_button);l.addLayout(g);l.addLayout(b);return c
    def _create_details_table_container(self):
        c=QFrame();c.setObjectName("container");l=QVBoxLayout(c);l.addWidget(QLabel("Detalhes dos Pontos",objectName="sectionTitle"));self.table=QTableWidget();self.table.setColumnCount(6);self.table.setHorizontalHeaderLabels(["Empresa","Cód ONS","Tensão","Ressalva?","Ação/Aprovado","Arquivo"]);h=self.table.horizontalHeader();h.setSectionResizeMode(QHeaderView.ResizeMode.Interactive);h.setStretchLastSection(True);self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers);self.table.cellClicked.connect(self.link_clicked.emit);self.table.setFixedHeight((self.fontMetrics().height()+12)*16);l.addWidget(self.table);return c
    def _apply_filters(self):self.filters_applied.emit({"company":self.company_combo.currentText(),"search":self.search_input.text(),"year":self.year_combo.currentText(),"tension":self.tension_combo.currentText(),"status":self.status_combo.currentText()})
    def _clear_filters(self):self.company_combo.setCurrentIndex(0);self.search_input.clear();self.year_combo.setCurrentIndex(0);self.tension_combo.setCurrentIndex(0);self.status_combo.setCurrentIndex(0);self._apply_filters()
    def update_kpis(self,d):
        self.kpi_cards["uc"].findChild(QLabel,"kpiValue").setText(str(d.get('unique_companies',0)))
        self.kpi_cards["tp"].findChild(QLabel,"kpiValue").setText(str(d.get('total_points',0)))
        self.kpi_cards["pr"].findChild(QLabel,"kpiValue").setText(str(d.get('points_with_remarks',0)))
        self.kpi_cards["ppr"].findChild(QLabel,"kpiValue").setText(str(d.get('percentage_with_remarks','0.0%')))
    def populate_company_analysis(self,d):
        for i in reversed(range(self.company_analysis_layout.count())): self.company_analysis_layout.itemAt(i).widget().setParent(None)
        r,c=0,0
        for s in d: card=CompanyCard(s['nome_empresa'],s);self.company_analysis_layout.addWidget(card,r,c);c+=1;
            if c>=3:c,r=0,r+1
    def populate_yearly_stats(self,d):
        for i in reversed(range(self.yearly_stats_layout.count())): self.yearly_stats_layout.itemAt(i).widget().setParent(None)
        r,c=0,0
        for y,s in d.items():card=QFrame();card.setObjectName("kpiCard");l=QVBoxLayout(card);yl=QLabel(f"Ano:{y}");p=QLabel(f"Ponta:{s.get('ponta',0):,.2f}");f=QLabel(f"Fora Ponta:{s.get('fora_ponta',0):,.2f}");l.addWidget(yl);l.addWidget(p);l.addWidget(f);self.yearly_stats_layout.addWidget(card,r,c);c+=1;
            if c>=4:c,r=0,r+1
    def populate_filters(self,c,t):self.company_combo.addItems(["Todas"]+c);self.year_combo.addItems(["Todos","2025","2026","2027","2028"]);self.tension_combo.addItems(["Todas"]+t);self.status_combo.addItems(["Todos","Com Ressalva","Aprovado"])
    def populate_table(self,d):
        self.table.setRowCount(0);self.table.setRowCount(len(d))
        for r,row in enumerate(d):
            self.table.setItem(r,0,QTableWidgetItem(row['nome_empresa']));self.table.setItem(r,1,QTableWidgetItem(row['cod_ons']));self.table.setItem(r,2,QTableWidgetItem(str(row.get('tensao_kv','N/D'))))
            hr=row.get('anotacao_geral')and str(row.get('anotacao_geral')).strip().lower()not in('','nan')
            if hr:btn=QPushButton("Sim");btn.setStyleSheet("background-color:#FBBF24;color:#78350F;");btn.clicked.connect(lambda c=False,r=r:self.details_requested.emit(r));self.table.setCellWidget(r,3,btn)
            else:item=QTableWidgetItem("Não");item.setForeground(Qt.GlobalColor.green);self.table.setItem(r,3,item)
            if row.get('aprovado_por'):self.table.setCellWidget(r,4,QLabel(f"{row['aprovado_por']}"))
            else:btn=QPushButton("Aprovar");btn.clicked.connect(lambda c=False,r=r:self.approve_requested.emit(r));self.table.setCellWidget(r,4,btn)
            link=row.get('arquivo_referencia','');item=QTableWidgetItem("Abrir" if link else "N/D");
            if link:item.setData(Qt.ItemDataRole.UserRole,link);item.setForeground(Qt.GlobalColor.cyan)
            self.table.setItem(r,5,item)
        self.table.resizeRowsToContents()

class GraphicsWidget(QWidget):
    def __init__(self,parent=None):super().__init__(parent);self._setup_ui()
    def _setup_ui(self):l=QVBoxLayout(self);l.setContentsMargins(20,20,20,20);t=QLabel("Análise Gráfica");t.setObjectName("headerTitle");l.addWidget(t);self.grid_layout=QGridLayout();l.addLayout(self.grid_layout)
    def populate_charts(self,d):
        if not px or not QWebEngineView:return
        self.pc=self._create_plotly_chart(d.get('points_per_company'),self._plot_points);self.rc=self._create_plotly_chart(d.get('remarks_summary'),self._plot_remarks);self.yc=self._create_plotly_chart(d.get('yearly_sum'),self._plot_yearly)
        self.grid_layout.addWidget(self.pc,0,0);self.grid_layout.addWidget(self.rc,0,1);self.grid_layout.addWidget(self.yc,1,0,1,2)
    def _create_plotly_chart(self,d,p):b=QWebEngineView();
        if d is None:return b
        f=p(d);tf=tempfile.NamedTemporaryFile(suffix=".html",delete=False,mode='w',encoding='utf-8');f.write_html(tf.name,config={'displayModeBar':False});tf.close();b.setUrl(QUrl.fromLocalFile(os.path.abspath(tf.name)));return b
    def _get_plotly_layout(self,t):return go.Layout(title={'text':t,'x':0.5,'font':{'color':'white'}},paper_bgcolor='#1F2937',plot_bgcolor='#1F2937',font={'color':'#E0E0E0'},xaxis={'gridcolor':'#374151'},yaxis={'gridcolor':'#374151'})
    def _plot_points(self,d):df=pd.DataFrame(d);f=px.bar(df,y='nome_empresa',x='count',orientation='h',labels={'count':'Nº Pontos','nome_empresa':'Empresa'},color_discrete_sequence=['#EA580C']);f.update_layout(self._get_plotly_layout("Pontos por Empresa"));return f
    def _plot_remarks(self,d):
        if not d:return go.Figure()
        w,a=d.get('with_remarks',0),d.get('total',0)-w;l=['Sem','Com'];v=[a,w];f=go.Figure(data=[go.Pie(labels=l,values=v,hole=.4,marker_colors=['#22C55E','#F97316'])]);f.update_layout(self._get_plotly_layout("Proporção de Ressalvas"));return f
    def _plot_yearly(self,d):df=pd.DataFrame(d);f=px.bar(df,x='ano',y='total_valor',labels={'ano':'Ano','total_valor':'Soma MUST'},color_discrete_sequence=['#3B82F6']);f.update_layout(self._get_plotly_layout("Soma MUST por Ano"),xaxis={'type':'category'});return f

class ReportsWidget(QWidget):
    def __init__(self,parent=None):super().__init__(parent);l=QVBoxLayout(self);l.setContentsMargins(20,20,20,20);t=QLabel("Relatórios");t.setObjectName("headerTitle");s=QLabel("Geração de relatórios.");s.setObjectName("headerSubtitle");l.addWidget(t);l.addWidget(s);l.addStretch()

class SettingsWidget(QWidget):
    theme_selection_changed=Signal(str)
    def __init__(self,parent=None):super().__init__(parent);self._setup_ui()
    def _setup_ui(self):
        ml=QVBoxLayout(self);ml.setContentsMargins(20,20,20,20);ml.setAlignment(Qt.AlignmentFlag.AlignTop);t=QLabel("Configurações");t.setObjectName("headerTitle");ml.addWidget(t);c=QFrame();c.setObjectName("container");cl=QVBoxLayout(c);ml.addWidget(c);tl=QHBoxLayout();tl.addWidget(QLabel("Tema:"));self.tc=QComboBox();self.tc.addItem("Escuro","dark");self.tc.addItem("Claro","light");self.tc.currentIndexChanged.connect(self._on_theme_changed);tl.addWidget(self.tc);cl.addLayout(tl)
    def _on_theme_changed(self,i):self.theme_selection_changed.emit(self.tc.itemData(i))
    def set_theme(self,theme_name):i=self.tc.findData(theme_name);
        if i>=0:self.tc.setCurrentIndex(i)

# ==============================================================================
# JANELA PRINCIPAL (VIEW SHELL)
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):super().__init__();self.setWindowTitle("Dashboard MUST");self.setMinimumSize(1400,950);self._setup_ui()
    def _setup_ui(self):
        cw=QWidget();self.setCentralWidget(cw);ml=QHBoxLayout(cw);self.np=self._create_nav_panel();ml.addWidget(self.np);self.sw=QStackedWidget();ml.addWidget(self.sw,1)
    def add_view(self,w):s=QScrollArea();s.setWidgetResizable(True);s.setWidget(w);s.setStyleSheet("border:none;");self.sw.addWidget(s);return w
    def _create_nav_panel(self):
        n=QFrame();n.setObjectName("navPanel");n.setFixedWidth(240);l=QVBoxLayout(n);t=QLabel("Menu");t.setObjectName("headerTitle");l.addWidget(t)
        self.nav_buttons=QListWidget();l.addWidget(self.nav_buttons);l.addStretch();l.addWidget(QLabel("v1.2",styleSheet="color:#6B7280;"));return n
    def add_nav_button(self,t):self.nav_buttons.addItem(QListWidgetItem(t))
    def apply_theme(self,t):self.setStyleSheet(DARK_STYLE if t=="dark" else LIGHT_STYLE)

# ==============================================================================
# CONTROLLER
# ==============================================================================
class AppController:
    def __init__(self,models,view):
        self._db=models['db_model'];self._sm=models['settings_model'];self._v=view
        self._setup_views();self._connect_signals();self.on_theme_changed(self._sm.theme);self._sv.set_theme(self._sm.theme);self.load_initial_data()
    def _setup_views(self):
        self._dv=self._v.add_view(DashboardMainWidget());self._gv=self._v.add_view(GraphicsWidget());self._ev=self._v.add_view(PDFExtractionWidget());self._rv=self._v.add_view(ReportsWidget());self._sv=self._v.add_view(SettingsWidget())
        self._v.add_nav_button("Dashboard");self._v.add_nav_button("Gráficos");self._v.add_nav_button("Extração");self._v.add_nav_button("Relatórios");self._v.add_nav_button("Configurações")
        self._v.nav_buttons.setCurrentRow(0)
    def _connect_signals(self):
        self._v.nav_buttons.currentRowChanged.connect(self._v.sw.setCurrentIndex);self._dv.filters_applied.connect(self.on_filters_changed);self._dv.approve_requested.connect(self.on_approve_requested)
        self._dv.details_requested.connect(self.on_details_requested);self._dv.link_clicked.connect(self.on_link_clicked);self._sv.theme_selection_changed.connect(self.on_theme_changed);self._sm.theme_changed.connect(self._v.apply_theme)
    def load_initial_data(self):
        self._dv.update_kpis(self._db.get_kpi_summary());self._dv.populate_company_analysis(self._db.get_company_analysis())
        stats=self._db.get_yearly_must_stats();yt={};[yt.setdefault(r['ano'],{}).update({r['periodo']:r.get('total_valor',0)}) for r in stats];self._dv.populate_yearly_stats(yt)
        self._dv.populate_filters(self._db.get_unique_companies(),self._db.get_unique_tensions());self._gv.populate_charts(self._db.get_data_for_charts());self.on_filters_changed({})
    def on_filters_changed(self,f):self._dv.populate_table(self._db.get_all_connection_points(f))
    def on_approve_requested(self,r):
        cod=self._dv.table.item(r,1).text();d=ApprovalDialog(cod,self._v)
        if d.exec():
            if self._db.approve_point(cod,d.approver_name):self._dv._apply_filters()
    - [ ] 
    def on_details_requested(self,r):
        cod=self._dv.table.item(r,1).text();ad=self._db._execute_query(f"SELECT anotacao_geral FROM {self._db.tbl_anotacao} WHERE cod_ons = ?",(cod,),fetch_one=True)
        a=ad.get('anotacao_geral')if ad else "N/A";h=self._db.get_must_history_for_point(cod);DetailsDialog(str(a),h,self._v).exec()
    def on_link_clicked(self,r,c):
        if c==5:item=self._dv.table.item(r,c);
            if item and item.data(Qt.ItemDataRole.UserRole):webbrowser.open(item.data(Qt.ItemDataRole.UserRole))
    def on_theme_changed(self,t):self._sm.theme=t

# ==============================================================================
# PONTO DE ENTRADA
# ==============================================================================
def setup_logging():logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] - %(message)s")
def main():
    setup_logging();app=QApplication(sys.argv);db_folder=Path("./database").resolve()
    access,sqlite=db_folder/"Database_MUST.accdb",db_folder/"database_consolidado.db";db_to_use=None
    if access.exists():
        try:pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"fr"DBQ={access};");db_to_use=access
        except pyodbc.Error:pass
    if not db_to_use and sqlite.exists():db_to_use=sqlite
    if not db_to_use:QMessageBox.critical(None,"Erro",f"BD não encontrado em:\n{db_folder}");sys.exit(1)
    try:
        db_model=DashboardDB(db_to_use);settings_model=SettingsModel()
        main_view=MainWindow();controller=AppController(models={'db_model':db_model,'settings_model':settings_model},view=main_view)
        main_view.show();sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Erro fatal: {e}",exc_info=True);QMessageBox.critical(None,"Erro",f"Erro:\n{e}");sys.exit(1)

if __name__=='__main__':
    main()

