import sys
import sqlite3
import webbrowser
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QFrame, QDialog, QTextBrowser, QTabWidget,
    QProgressBar, QStackedWidget,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

# Adiciona dependência para gráficos. É necessário instalar: pip install matplotlib
try:
    import matplotlib
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    matplotlib.use('QtAgg')
except ImportError:
    print("Matplotlib não encontrado. Gráficos não estarão disponíveis. Instale com: pip install matplotlib")
    FigureCanvas = None

# --- PARTE 1: MODELO DE DADOS (LÓGICA DO BANCO DE DADOS) ---

class DashboardDB:
    """
    Model (Parte do MVC): Manipula todas as interações de LEITURA e ESCRITA com o banco de dados.
    """
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"O arquivo de banco de dados não foi encontrado: {self.db_path}\n"
                "Certifique-se de que o caminho está correto e o banco de dados já foi criado."
            )
        self._ensure_approval_columns_exist()
        
        self.company_links = {
            'SUL SUDESTE': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EbWWq1r7MnxPvOejycbr82cB5a_rN_PCsDMDjp9r3bF3Ng?e=C7dxKN',
            'ELETROPAULO': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EXzdo_ClziVDrnOHTiGzoysBdqgci92tpuKYN2xKIjPQvw?e=kzrFho',
            'PIRATININGA': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EZGF1uzc1opGujAlp1fwNqcBoLnXsAt532XFPbNrNCwEvQ?e=nEOCn9',
            'NEOENERGIA ELEKTRO': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/Eet4gEXFfDNEoPMejiLnMaQBVW1ubN1TxOIvMtLY0yUfPA?e=WruSdk',
            'JAGUARI': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EXzdo_ClziVDrnOHTiGzoysBdqgci92tpuKYN2xKIjPQvw?e=b2yXV2',
            'CPFL PAULISTA': 'https://onsbr-my.sharepoint.com/:b:/g/personal/pedrovictor_veras_ons_org_br/EbWWq1r7MnxPvOejycbr82cB5a_rN_PCsDMDjp9r3bF3Ng?e=C7dxKN'
        }

    def _execute_query(self, query, params=(), fetch_one=False):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Erro de banco de dados (leitura): {e}")
            return [] if not fetch_one else None

    def _execute_write_query(self, query, params=()):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro de banco de dados (escrita): {e}")
            return False

    def _ensure_approval_columns_exist(self):
        try:
            table_info = self._execute_query("PRAGMA table_info(anotacao)")
            column_names = [col['name'] for col in table_info]
            if 'aprovado_por' not in column_names:
                print("Adicionando coluna 'aprovado_por'...")
                self._execute_write_query("ALTER TABLE anotacao ADD COLUMN aprovado_por TEXT;")
            if 'data_aprovacao' not in column_names:
                print("Adicionando coluna 'data_aprovacao'...")
                self._execute_write_query("ALTER TABLE anotacao ADD COLUMN data_aprovacao TEXT;")
        except Exception as e:
            print(f"Não foi possível verificar/modificar a tabela 'anotacao': {e}")
            
    def get_kpi_summary(self):
        query_companies = "SELECT COUNT(DISTINCT id_empresa) as count FROM empresas;"
        query_points = "SELECT COUNT(*) as count FROM anotacao;"
        query_remarks = "SELECT COUNT(*) as count FROM anotacao WHERE anotacao_geral IS NOT NULL AND anotacao_geral != '' AND anotacao_geral != 'nan';"
        try:
            total_companies = self._execute_query(query_companies, fetch_one=True)['count']
            total_points = self._execute_query(query_points, fetch_one=True)['count']
            points_with_remarks = self._execute_query(query_remarks, fetch_one=True)['count']
            percentage = (points_with_remarks / total_points * 100) if total_points > 0 else 0
            return {'unique_companies': total_companies, 'total_points': total_points, 'points_with_remarks': points_with_remarks, 'percentage_with_remarks': f"{percentage:.1f}%"}
        except (TypeError, KeyError, ZeroDivisionError) as e:
            print(f"Erro ao calcular KPIs: {e}")
            return {'unique_companies': 0, 'total_points': 0, 'points_with_remarks': 0, 'percentage_with_remarks': '0.0%'}

    def get_company_analysis(self):
        query = """
            SELECT e.nome_empresa, COUNT(a.id_conexao) as total,
                   SUM(CASE WHEN a.anotacao_geral IS NOT NULL AND a.anotacao_geral != '' AND a.anotacao_geral != 'nan' THEN 1 ELSE 0 END) as with_remarks
            FROM empresas e JOIN anotacao a ON e.id_empresa = a.id_empresa
            GROUP BY e.nome_empresa ORDER BY e.nome_empresa;
        """
        return self._execute_query(query)
        
    def get_yearly_must_stats(self):
        query = "SELECT ano, periodo, SUM(valor) as total_valor FROM valores_must GROUP BY ano, periodo ORDER BY ano, periodo;"
        return self._execute_query(query)

    def get_unique_companies(self):
        query = "SELECT nome_empresa FROM empresas ORDER BY nome_empresa;"
        return [row['nome_empresa'] for row in self._execute_query(query)]

    def get_unique_tensions(self):
        query = "SELECT DISTINCT tensao_kv FROM anotacao WHERE tensao_kv IS NOT NULL ORDER BY tensao_kv;"
        return [str(row['tensao_kv']) for row in self._execute_query(query)]

    def get_all_connection_points(self, filters=None):
        query = """
            SELECT emp.nome_empresa, a.cod_ons, a.tensao_kv, a.anotacao_geral, a.aprovado_por, a.data_aprovacao
            FROM anotacao a JOIN empresas emp ON a.id_empresa = emp.id_empresa
        """
        conditions, params = [], []
        
        year_filter = filters.get("year") if filters else None
        if year_filter and year_filter != "Todos":
            conditions.append("EXISTS (SELECT 1 FROM valores_must vm WHERE vm.id_conexao = a.id_conexao AND vm.ano = ?)")
            params.append(int(year_filter))
            
        if filters:
            if filters.get("company") and filters["company"] != "Todas":
                conditions.append("emp.nome_empresa = ?"); params.append(filters["company"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"; conditions.append("(a.cod_ons LIKE ? OR a.anotacao_geral LIKE ?)"); params.extend([search_term, search_term])
            if filters.get("tension") and filters["tension"] != "Todas":
                conditions.append("a.tensao_kv = ?"); params.append(int(filters["tension"]))
            if filters.get("status") == "Com Ressalva":
                conditions.append("(a.anotacao_geral IS NOT NULL AND a.anotacao_geral != '' AND a.anotacao_geral != 'nan')")
            elif filters.get("status") == "Aprovado":
                 conditions.append("(a.anotacao_geral IS NULL OR a.anotacao_geral = '' OR a.anotacao_geral = 'nan')")
        
        if conditions: query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY a.id_conexao ORDER BY emp.nome_empresa, a.cod_ons;"
        
        results = self._execute_query(query, tuple(params))
        for row in results:
            normalized_empresa = str(row['nome_empresa']).strip().upper()
            row['arquivo_referencia'] = self.company_links.get(normalized_empresa, '')
        return results

    def get_must_history_for_point(self, cod_ons):
        query = "SELECT vm.ano, vm.periodo, vm.valor FROM valores_must vm JOIN anotacao a ON vm.id_conexao = a.id_conexao WHERE a.cod_ons = ? ORDER BY vm.ano, vm.periodo;"
        return self._execute_query(query, (cod_ons,))

    def approve_point(self, cod_ons, approver_name):
        query = "UPDATE anotacao SET aprovado_por = ?, data_aprovacao = ? WHERE cod_ons = ?;"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self._execute_write_query(query, (approver_name, timestamp, cod_ons))
        
    def get_data_for_charts(self):
        points_per_company = self._execute_query("SELECT e.nome_empresa, COUNT(a.id_conexao) as count FROM empresas e JOIN anotacao a ON e.id_empresa = a.id_empresa GROUP BY e.nome_empresa")
        remarks_summary = self._execute_query("SELECT SUM(CASE WHEN anotacao_geral IS NOT NULL AND anotacao_geral != '' AND anotacao_geral != 'nan' THEN 1 ELSE 0 END) as with_remarks, COUNT(id_conexao) as total FROM anotacao", fetch_one=True)
        yearly_sum = self._execute_query("SELECT ano, SUM(valor) as total_valor FROM valores_must GROUP BY ano ORDER BY ano")
        return {
            "points_per_company": points_per_company,
            "remarks_summary": remarks_summary,
            "yearly_sum": yearly_sum,
        }

# --- PARTE 2: VIEW / CONTROLLER (LÓGICA DA INTERFACE GRÁFICA) ---

STYLESHEET = """
QWidget { font-family: Inter, sans-serif; color: #E0E0E0; background-color: #111827; }
QMainWindow { background-color: #111827; }
QLabel { background-color: transparent; }
QLabel#headerTitle { font-size: 28px; font-weight: bold; }
QLabel#headerSubtitle { color: #9CA3AF; }
QLabel#sectionTitle { font-size: 18px; font-weight: bold; margin-bottom: 10px; margin-left: 5px;}
QFrame#kpiCard, QFrame#navPanel, QFrame#container { background-color: #1F2937; border-radius: 8px; }
QLabel#kpiTitle { color: #9CA3AF; font-size: 12px; }
QLabel#kpiValue { font-size: 26px; font-weight: bold; }
QLineEdit, QComboBox { background-color: #374151; border: 1px solid #4B5563; border-radius: 6px; padding: 8px; font-size: 14px; }
QLineEdit:focus, QComboBox:focus { border-color: #3B82F6; }
QPushButton { border-radius: 6px; padding: 8px 16px; font-size: 14px; font-weight: bold; text-align: left; }
QPushButton#navButton { background-color: transparent; border: none; padding: 12px; }
QPushButton#navButton:hover { background-color: #374151; }
QPushButton#navButton:checked { background-color: #3B82F6; color: white; }
QPushButton#filterButton { background-color: #EA580C; color: white; text-align: center; }
QPushButton#filterButton:hover { background-color: #F97316; }
QPushButton#clearButton { background-color: transparent; border: 1px solid #6B7280; text-align: center; }
QPushButton#clearButton:hover { background-color: #374151; }
QTableWidget { background-color: #1F2937; border: none; gridline-color: #374151; }
QHeaderView::section { background-color: #374151; color: #D1D5DB; padding: 8px; border: none; font-weight: bold; }
QTableWidget::item { padding-left: 10px; border-bottom: 1px solid #374151; }
QScrollBar:vertical, QScrollBar:horizontal { background: #1f2937; width: 10px; height: 10px; margin: 0; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background: #4b5563; min-width: 20px; border-radius: 5px; }
QTabWidget::pane { border: none; } QTabBar::tab { background: #1F2937; padding: 10px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
QTabBar::tab:selected { background: #374151; color: white; }
QProgressBar { border: 1px solid #4B5563; border-radius: 5px; text-align: center; color: #E0E0E0; background-color: #374151; }
QProgressBar::chunk { background-color: #F97316; border-radius: 4px; }
"""

class DetailsDialog(QDialog):
    def __init__(self, annotation_content, history_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes do Ponto de Conexão")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        tab_widget = QTabWidget()

        ressalva_widget = QWidget()
        ressalva_layout = QVBoxLayout(ressalva_widget)
        text_view = QTextBrowser()
        text_view.setPlainText(annotation_content if annotation_content else "Nenhuma ressalva para este ponto.")
        ressalva_layout.addWidget(text_view)
        
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_table = QTableWidget()
        history_table.setColumnCount(3)
        history_table.setHorizontalHeaderLabels(["Ano", "Período", "Valor MUST"])
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        history_table.setRowCount(len(history_data))
        for i, row in enumerate(history_data):
            valor = row.get('valor')
            valor_str = f"{float(valor):.2f}" if valor is not None else "N/D"
            history_table.setItem(i, 0, QTableWidgetItem(str(row['ano'])))
            history_table.setItem(i, 1, QTableWidgetItem(str(row['periodo'])))
            history_table.setItem(i, 2, QTableWidgetItem(valor_str))
        history_layout.addWidget(history_table)
        
        tab_widget.addTab(ressalva_widget, "Ressalva")
        tab_widget.addTab(history_widget, "Histórico de Valores")
        
        closeButton = QPushButton("Fechar"); closeButton.clicked.connect(self.accept)
        layout.addWidget(tab_widget); layout.addWidget(closeButton, 0, Qt.AlignmentFlag.AlignRight)

class ApprovalDialog(QDialog):
    def __init__(self, cod_ons, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aprovar Solicitação")
        self.setStyleSheet(STYLESHEET)
        self.setMinimumWidth(400)
        self.approver_name = ""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Ponto de Conexão:</b> {cod_ons}"))
        layout.addWidget(QLabel("Digite seu nome para confirmar a aprovação:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do Responsável")
        layout.addWidget(self.name_input)
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("Confirmar Aprovação"); self.confirm_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancelar"); self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.confirm_button); button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    def accept(self):
        if self.name_input.text().strip():
            self.approver_name = self.name_input.text().strip()
            super().accept()
        else:
            self.name_input.setStyleSheet("border: 1px solid red;")

class CompanyCard(QFrame):
    def __init__(self, company_name, stats, parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        with_remarks, total = stats.get('with_remarks', 0), stats.get('total', 0)
        percentage = (with_remarks / total * 100) if total > 0 else 0
        layout, name_label = QVBoxLayout(self), QLabel(company_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        stats_label = QLabel(f"Com Ressalvas: {with_remarks} / {total}"); stats_label.setObjectName("kpiTitle")
        self.progress_bar = QProgressBar(); self.progress_bar.setValue(int(percentage)); self.progress_bar.setFormat(f"{percentage:.1f}%")
        layout.addWidget(name_label); layout.addWidget(stats_label); layout.addWidget(self.progress_bar)

class DashboardApp(QMainWindow):
    def __init__(self, db_model):
        super().__init__()
        self.db = db_model
        self.setWindowTitle("Dashboard de Análise - Pontos MUST")
        self.setMinimumSize(1400, 950)
        self.setStyleSheet(STYLESHEET)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_hbox_layout = QHBoxLayout(central_widget)
        
        self.nav_panel = self._create_nav_panel()
        main_hbox_layout.addWidget(self.nav_panel)
        
        self.stacked_widget = QStackedWidget()
        main_hbox_layout.addWidget(self.stacked_widget, 1)
        
        self.dashboard_widget = self._create_main_dashboard_widget()
        self.graphics_widget = self._create_graphics_dashboard_widget()
        
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.stacked_widget.addWidget(self.graphics_widget)
        
        self._load_initial_data()
        self.nav_buttons["dashboard"].setChecked(True)

    def _create_nav_panel(self):
        nav_panel = QFrame(); nav_panel.setObjectName("navPanel"); nav_panel.setFixedWidth(220)
        nav_layout = QVBoxLayout(nav_panel)
        nav_title = QLabel("Menu"); nav_title.setObjectName("headerTitle")
        nav_layout.addWidget(nav_title)
        self.nav_buttons = {"dashboard": QPushButton(" Dashboard Principal"), "graphics": QPushButton(" Análise Gráfica")}
        for name, button in self.nav_buttons.items():
            button.setObjectName("navButton"); button.setCheckable(True); button.setAutoExclusive(True)
            nav_layout.addWidget(button)
        self.nav_buttons["dashboard"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.nav_buttons["graphics"].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        nav_layout.addStretch()
        return nav_panel

    def _create_main_dashboard_widget(self):
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20); self.main_layout.setSpacing(20)
        
        # Estrutura com containers
        self._create_header()
        self.main_layout.addWidget(self._create_kpi_container())
        self.main_layout.addWidget(self._create_company_analysis_container())
        self.main_layout.addWidget(self._create_yearly_stats_container())
        self.main_layout.addWidget(self._create_filters_container())
        self.main_layout.addWidget(self._create_details_table_container())
        self.main_layout.addStretch()

        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget); scroll_area.setStyleSheet("border: none;")
        return scroll_area

    # Funções containerizadas
    def _create_kpi_container(self):
        container = QFrame(); container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Visão Geral das Solicitações", objectName="sectionTitle"))
        self.kpi_layout = QHBoxLayout(); self.kpi_layout.setSpacing(20)
        self.kpi_cards = {
            "unique_companies": self._create_kpi_card("Total de Empresas", "0"),
            "total_points": self._create_kpi_card("Total de Pontos de Conexão", "0"),
            "points_with_remarks": self._create_kpi_card("Pontos com Ressalvas", "0"),
            "percentage_with_remarks": self._create_kpi_card("% de Pontos com Ressalvas", "0.0%"),
        }
        for card in self.kpi_cards.values(): self.kpi_layout.addWidget(card)
        layout.addLayout(self.kpi_layout)
        return container

    def _create_company_analysis_container(self):
        container = QFrame(); container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Análise por Empresa", objectName="sectionTitle"))
        self.company_analysis_layout = QGridLayout(); self.company_analysis_layout.setSpacing(20)
        layout.addLayout(self.company_analysis_layout)
        return container

    def _create_yearly_stats_container(self):
        container = QFrame(); container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Estatísticas Anuais MUST (Soma dos Valores)", objectName="sectionTitle"))
        self.yearly_stats_layout = QGridLayout(); self.yearly_stats_layout.setSpacing(20)
        layout.addLayout(self.yearly_stats_layout)
        return container

    def _create_filters_container(self):
        container = QFrame(); container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Filtros", objectName="sectionTitle"))
        grid_layout = QGridLayout(); grid_layout.setSpacing(15)
        grid_layout.addWidget(QLabel("Empresa"), 0, 0); grid_layout.addWidget(QLabel("Pesquisar"), 0, 1)
        grid_layout.addWidget(QLabel("Ano"), 0, 2); grid_layout.addWidget(QLabel("Tensão (kV)"), 0, 3); grid_layout.addWidget(QLabel("Status"), 0, 4)
        self.company_combo = QComboBox(); self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Cód ONS, Ressalva...")
        self.year_combo = QComboBox(); self.tension_combo = QComboBox(); self.status_combo = QComboBox()
        grid_layout.addWidget(self.company_combo, 1, 0); grid_layout.addWidget(self.search_input, 1, 1); grid_layout.addWidget(self.year_combo, 1, 2)
        grid_layout.addWidget(self.tension_combo, 1, 3); grid_layout.addWidget(self.status_combo, 1, 4)
        button_layout = QHBoxLayout(); button_layout.addStretch()
        self.clear_button = QPushButton("Limpar"); self.clear_button.setObjectName("clearButton"); self.clear_button.clicked.connect(self._clear_filters)
        self.filter_button = QPushButton("Filtrar"); self.filter_button.setObjectName("filterButton"); self.filter_button.clicked.connect(self._apply_filters)
        button_layout.addWidget(self.clear_button); button_layout.addWidget(self.filter_button)
        layout.addLayout(grid_layout); layout.addLayout(button_layout)
        return container

    def _create_details_table_container(self):
        container = QFrame(); container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Detalhes dos Pontos de Conexão", objectName="sectionTitle"))
        self.table = QTableWidget(); self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Empresa", "Cód ONS", "Tensão (kV)", "Ressalva?", "Ação/Aprovado Por", "Arquivo PDF"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.setFixedHeight((self.fontMetrics().height() + 12) * 16)
        layout.addWidget(self.table)
        return container

    def _create_graphics_dashboard_widget(self):
        if not FigureCanvas: return QLabel("Matplotlib não está instalado.\nA Análise Gráfica não está disponível.")
        graphics_widget = QWidget()
        layout = QVBoxLayout(graphics_widget)
        title = QLabel("Análise Gráfica"); title.setObjectName("headerTitle")
        layout.addWidget(title)
        chart_data = self.db.get_data_for_charts()
        grid_layout = QGridLayout(); grid_layout.setSpacing(20)
        grid_layout.addWidget(self._create_points_by_company_chart(chart_data['points_per_company']), 0, 0)
        grid_layout.addWidget(self._create_remarks_pie_chart(chart_data['remarks_summary']), 0, 1)
        grid_layout.addWidget(self._create_yearly_sum_chart(chart_data['yearly_sum']), 1, 0, 1, 2)
        layout.addLayout(grid_layout)
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(graphics_widget); scroll_area.setStyleSheet("border: none;")
        return scroll_area

    def _create_chart_canvas(self, fig_title, data, chart_func):
        fig = Figure(figsize=(8, 6), dpi=100); fig.patch.set_facecolor('#1F2937')
        ax = fig.add_subplot(111); ax.set_facecolor('#1F2937'); ax.tick_params(colors='#E0E0E0')
        ax.spines['bottom'].set_color('#E0E0E0'); ax.spines['left'].set_color('#E0E0E0')
        ax.spines['top'].set_color('none'); ax.spines['right'].set_color('none')
        ax.set_title(fig_title, color='#E0E0E0', fontsize=16); chart_func(ax, data); fig.tight_layout()
        return FigureCanvas(fig)

    def _create_points_by_company_chart(self, data):
        def plot(ax, data):
            companies = [d['nome_empresa'] for d in data]; counts = [d['count'] for d in data]
            ax.barh(companies, counts, color='#EA580C'); ax.set_xlabel('Nº de Pontos de Conexão', color='#9CA3AF')
        return self._create_chart_canvas("Pontos de Conexão por Empresa", data, plot)

    def _create_remarks_pie_chart(self, data):
        def plot(ax, data):
            with_remarks = data.get('with_remarks', 0); approved = data.get('total', 0) - with_remarks
            ax.pie([approved, with_remarks], labels=['Aprovados', 'Com Ressalva'], colors=['#22C55E', '#F97316'], autopct='%1.1f%%', startangle=90, textprops={'color': 'white', 'fontsize': 12})
        return self._create_chart_canvas("Proporção de Ressalvas", data, plot)

    def _create_yearly_sum_chart(self, data):
        def plot(ax, data):
            years = [d['ano'] for d in data]; totals = [d['total_valor'] for d in data]
            ax.bar(years, totals, color='#3B82F6'); ax.set_ylabel('Soma do Valor MUST', color='#9CA3AF'); ax.set_xticks(years)
        return self._create_chart_canvas("Soma do Valor MUST por Ano", data, plot)

    def _create_header(self):
        header_layout = QVBoxLayout()
        title = QLabel("Dashboard de Análise de Pontos MUST"); title.setObjectName("headerTitle")
        subtitle = QLabel("Visão geral das solicitações e ressalvas por empresa e ponto de conexão."); subtitle.setObjectName("headerSubtitle")
        header_layout.addWidget(title); header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)

    def _create_kpi_card(self, title_text, value_text):
        card = QFrame(); card.setObjectName("kpiCard")
        card_layout = QVBoxLayout(card)
        title, value = QLabel(title_text), QLabel(value_text)
        title.setObjectName("kpiTitle"); value.setObjectName("kpiValue")
        card_layout.addWidget(title); card_layout.addWidget(value)
        return card

    def _load_initial_data(self):
        self._update_kpis()
        self._populate_company_analysis()
        self._populate_yearly_stats()
        self._populate_filters()
        self._apply_filters()

    def _update_kpis(self):
        kpi_data = self.db.get_kpi_summary()
        self.kpi_cards["unique_companies"].findChild(QLabel, "kpiValue").setText(str(kpi_data.get('unique_companies', 0)))
        self.kpi_cards["total_points"].findChild(QLabel, "kpiValue").setText(str(kpi_data.get('total_points', 0)))
        self.kpi_cards["points_with_remarks"].findChild(QLabel, "kpiValue").setText(str(kpi_data.get('points_with_remarks', 0)))
        self.kpi_cards["percentage_with_remarks"].findChild(QLabel, "kpiValue").setText(str(kpi_data.get('percentage_with_remarks', '0.0%')))

    def _populate_company_analysis(self):
        analysis_data = self.db.get_company_analysis()
        for i in reversed(range(self.company_analysis_layout.count())): self.company_analysis_layout.itemAt(i).widget().setParent(None)
        row, col, MAX_COLS = 0, 0, 3
        for stats in analysis_data:
            card = CompanyCard(stats['nome_empresa'], stats)
            self.company_analysis_layout.addWidget(card, row, col)
            col += 1;
            if col >= MAX_COLS: col, row = 0, row + 1

    def _populate_yearly_stats(self):
        stats_data = self.db.get_yearly_must_stats()
        yearly_totals = {};
        for row in stats_data:
            if row['ano'] not in yearly_totals: yearly_totals[row['ano']] = {}
            yearly_totals[row['ano']][row['periodo']] = row['total_valor']
        row, col, MAX_COLS = 0, 0, 4
        for year in sorted(yearly_totals.keys()):
            card = QFrame(); card.setObjectName("kpiCard"); layout = QVBoxLayout(card)
            year_label = QLabel(f"Ano: {year}"); year_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            ponta_val, fora_ponta_val = yearly_totals[year].get('ponta', 0), yearly_totals[year].get('fora ponta', 0)
            ponta_label = QLabel(f"Ponta: {ponta_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")); fora_ponta_label = QLabel(f"Fora Ponta: {fora_ponta_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            ponta_label.setObjectName("kpiTitle"); fora_ponta_label.setObjectName("kpiTitle")
            layout.addWidget(year_label); layout.addWidget(ponta_label); layout.addWidget(fora_ponta_label)
            self.yearly_stats_layout.addWidget(card, row, col)
            col += 1
            if col >= MAX_COLS: col, row = 0, row + 1

    def _populate_filters(self):
        self.company_combo.addItems(["Todas"] + self.db.get_unique_companies())
        self.year_combo.addItems(["Todos", "2025", "2026", "2027", "2028"])
        self.tension_combo.addItems(["Todas"] + self.db.get_unique_tensions())
        self.status_combo.addItems(["Todos", "Com Ressalva", "Aprovado"])

    def _populate_table(self, data):
        self.table.setRowCount(0)
        self.table.setRowCount(len(data))
        for r, row in enumerate(data):
            annotation = row.get('anotacao_geral')
            has_remark = annotation and str(annotation).strip().lower() not in ('', 'nan')
            
            self.table.setItem(r, 0, QTableWidgetItem(row['nome_empresa'])); self.table.setItem(r, 1, QTableWidgetItem(row['cod_ons'])); self.table.setItem(r, 2, QTableWidgetItem(str(row['tensao_kv'])))
            
            if has_remark:
                remark_button = QPushButton("Sim")
                remark_button.setStyleSheet("background-color: #FBBF24; color: #78350F; font-weight: bold; text-align: center;")
                remark_button.clicked.connect(lambda checked=False, row=r: self._show_details_modal(row))
                self.table.setCellWidget(r, 3, remark_button)
            else:
                item = QTableWidgetItem("Não")
                item.setForeground(Qt.GlobalColor.green)
                self.table.setItem(r, 3, item)
            
            if row.get('aprovado_por'):
                self.table.setCellWidget(r, 4, QLabel(f"{row['aprovado_por']} em {row['data_aprovacao']}"))
            else:
                approve_button = QPushButton("Aprovar"); approve_button.setStyleSheet("font-size: 12px; padding: 5px; text-align: center; border: 1px solid #6B7280;")
                approve_button.clicked.connect(lambda checked=False, row=r: self._open_approval_dialog(row))
                self.table.setCellWidget(r, 4, approve_button)
            
            pdf_link = row.get('arquivo_referencia', '')
            pdf_item = QTableWidgetItem("Abrir Link" if pdf_link else "N/D")
            if pdf_link: pdf_item.setForeground(Qt.GlobalColor.cyan); pdf_item.setData(Qt.ItemDataRole.UserRole, pdf_link)
            self.table.setItem(r, 5, pdf_item)
        
        self.table.resizeRowsToContents()

    def _apply_filters(self):
        filters = {"company": self.company_combo.currentText(), "search": self.search_input.text(), "year": self.year_combo.currentText(), "tension": self.tension_combo.currentText(), "status": self.status_combo.currentText()}
        data = self.db.get_all_connection_points(filters)
        self._populate_table(data)
    
    def _clear_filters(self):
        self.company_combo.setCurrentIndex(0); self.search_input.clear(); self.year_combo.setCurrentIndex(0)
        self.tension_combo.setCurrentIndex(0); self.status_combo.setCurrentIndex(0); self._apply_filters()

    def _on_cell_clicked(self, row, column):
        if column == 5:
            item = self.table.item(row, column)
            if item and item.data(Qt.ItemDataRole.UserRole): webbrowser.open(item.data(Qt.ItemDataRole.UserRole))

    def _open_approval_dialog(self, row):
        cod_ons = self.table.item(row, 1).text()
        dialog = ApprovalDialog(cod_ons, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            approver = dialog.approver_name
            if self.db.approve_point(cod_ons, approver):
                self._apply_filters()

    def _show_details_modal(self, row):
        cod_ons_item = self.table.item(row, 1)
        if not cod_ons_item: return
        cod_ons = cod_ons_item.text()
        annotation_data = self.db._execute_query("SELECT anotacao_geral FROM anotacao WHERE cod_ons = ?", (cod_ons,), fetch_one=True)
        annotation = annotation_data.get('anotacao_geral') if annotation_data else "Anotação não encontrada."
        history_data = self.db.get_must_history_for_point(cod_ons)
        dialog = DetailsDialog(str(annotation), history_data, self); dialog.exec()

# --- PARTE 3: PONTO DE ENTRADA DA APLICAÇÃO ---

if __name__ == '__main__':
    app = QApplication(sys.argv)
    db_path = Path(r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\AUTOMACÕES ONS\arquivos\database\database_consolidado.db")
    try:
        db_model = DashboardDB(db_path)
        window = DashboardApp(db_model)
        window.show()
        sys.exit(app.exec())
    except FileNotFoundError as e:
        error_dialog = QDialog(); error_dialog.setWindowTitle("Erro Crítico")
        layout = QVBoxLayout(); label = QLabel(str(e))
        layout.addWidget(label); error_dialog.setLayout(layout)
        error_dialog.exec(); sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        sys.exit(1)

