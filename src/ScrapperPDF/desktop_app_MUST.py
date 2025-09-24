import sys
import sqlite3
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QFrame, QDialog, QTextBrowser
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# --- PARTE 1: MODELO DE DADOS (LÓGICA DO BANCO DE DADOS) ---

class DashboardDB:
    """
    Model (Parte do MVC): Manipula todas as interações de LEITURA com o banco de dados para o dashboard.
    """
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"O arquivo de banco de dados não foi encontrado: {self.db_path}\n"
                "Certifique-se de que o caminho está correto e o banco de dados já foi criado."
            )

    def _execute_query(self, query, params=(), fetch_one=False):
        """Função auxiliar para executar consultas e buscar resultados."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Acessa colunas pelo nome
                cursor = conn.cursor()
                cursor.execute(query, params)
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"Erro de banco de dados: {e}")
            return [] if not fetch_one else None

    def get_kpi_summary(self):
        """Busca dados para os cartões principais de KPIs."""
        query_companies = "SELECT COUNT(DISTINCT id_empresa) as count FROM empresas;"
        query_points = "SELECT COUNT(*) as count FROM anotacao;"
        query_remarks = "SELECT COUNT(*) as count FROM anotacao WHERE anotacao_geral IS NOT NULL AND anotacao_geral != '' AND anotacao_geral != 'nan';"
        
        try:
            total_companies = self._execute_query(query_companies, fetch_one=True)['count']
            total_points = self._execute_query(query_points, fetch_one=True)['count']
            points_with_remarks = self._execute_query(query_remarks, fetch_one=True)['count']
            
            percentage = (points_with_remarks / total_points * 100) if total_points > 0 else 0

            return {
                'unique_companies': total_companies,
                'total_points': total_points,
                'points_with_remarks': points_with_remarks,
                'percentage_with_remarks': f"{percentage:.1f}%"
            }
        except (TypeError, KeyError, ZeroDivisionError) as e:
            print(f"Erro ao calcular KPIs: {e}")
            return {
                'unique_companies': 0, 'total_points': 0,
                'points_with_remarks': 0, 'percentage_with_remarks': '0.0%'
            }

    def get_company_analysis(self):
        """Calcula o total de pontos e pontos com ressalvas para cada empresa."""
        query = """
            SELECT
                e.nome_empresa,
                COUNT(a.id_conexao) as total,
                SUM(CASE WHEN a.anotacao_geral IS NOT NULL AND a.anotacao_geral != '' AND a.anotacao_geral != 'nan' THEN 1 ELSE 0 END) as with_remarks
            FROM empresas e
            JOIN anotacao a ON e.id_empresa = a.id_empresa
            GROUP BY e.nome_empresa
            ORDER BY e.nome_empresa;
        """
        return self._execute_query(query)

    def get_unique_companies(self):
        """Obtém uma lista ordenada de todos os nomes de empresas únicos."""
        query = "SELECT nome_empresa FROM empresas ORDER BY nome_empresa;"
        results = self._execute_query(query)
        return [row['nome_empresa'] for row in results]

    def get_all_connection_points(self, filters=None):
        """
        Busca dados detalhados dos pontos de conexão, aplicando filtros opcionais.
        """
        query = """
            SELECT
                emp.nome_empresa,
                a.cod_ons,
                a.tensao_kv,
                a.anotacao_geral
            FROM anotacao a
            JOIN empresas emp ON a.id_empresa = emp.id_empresa
        """
        conditions = []
        params = []

        if filters:
            if filters.get("company") and filters["company"] != "Todas":
                conditions.append("emp.nome_empresa = ?")
                params.append(filters["company"])
            
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                conditions.append("(a.cod_ons LIKE ? OR a.anotacao_geral LIKE ?)")
                params.extend([search_term, search_term])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY emp.nome_empresa, a.cod_ons;"

        return self._execute_query(query, params)

# --- PARTE 2: VIEW / CONTROLLER (LÓGICA DA INTERFACE GRÁFICA) ---

# --- Folha de Estilos (Stylesheet) ---
STYLESHEET = """
QWidget {
    font-family: Inter, sans-serif;
    color: #E0E0E0;
    background-color: #111827; /* Dark Blue-Gray */
}
QMainWindow {
    background-color: #111827;
}
QLabel {
    background-color: transparent;
}
QLabel#headerTitle {
    font-size: 28px;
    font-weight: bold;
}
QLabel#headerSubtitle {
    color: #9CA3AF; /* Gray */
}
QLabel#sectionTitle {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}
QFrame#kpiCard {
    background-color: #1F2937; /* Lighter Blue-Gray */
    border-radius: 8px;
}
QLabel#kpiTitle {
    color: #9CA3AF;
    font-size: 12px;
}
QLabel#kpiValue {
    font-size: 26px;
    font-weight: bold;
}
QFrame#filterFrame {
    background-color: #1F2937;
    border-radius: 8px;
}
QLineEdit, QComboBox {
    background-color: #374151; /* Gray */
    border: 1px solid #4B5563;
    border-radius: 6px;
    padding: 8px;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #3B82F6; /* Blue */
}
QComboBox::drop-down {
    border: none;
}
QPushButton {
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton#filterButton {
    background-color: #EA580C; /* Orange */
    color: white;
}
QPushButton#filterButton:hover {
    background-color: #F97316;
}
QPushButton#clearButton {
    background-color: transparent;
    border: 1px solid #6B7280;
}
QPushButton#clearButton:hover {
    background-color: #374151;
}
QTableWidget {
    background-color: #1F2937;
    border: none;
    border-radius: 8px;
    gridline-color: #374151;
}
QHeaderView::section {
    background-color: #374151;
    color: #D1D5DB;
    padding: 8px;
    border: none;
    font-weight: bold;
    text-transform: uppercase;
}
QTableWidget::item {
    padding-left: 10px;
    border-bottom: 1px solid #374151;
}
QTableWidget::item:selected {
    background-color: #3B82F6;
    color: white;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #1f2937;
    width: 10px;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #4b5563;
    min-height: 20px;
    min-width: 20px;
    border-radius: 5px;
}
QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
}
"""

class AnnotationDialog(QDialog):
    """Um diálogo modal para exibir o texto detalhado da anotação."""
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes da Ressalva")
        self.setMinimumSize(600, 400)
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        
        self.textView = QTextBrowser()
        self.textView.setPlainText(content)
        self.textView.setStyleSheet("background-color: #374151; border-radius: 6px; padding: 10px;")
        
        closeButton = QPushButton("Fechar")
        closeButton.clicked.connect(self.accept)
        
        layout.addWidget(self.textView)
        layout.addWidget(closeButton, 0, Qt.AlignmentFlag.AlignRight)

class DashboardApp(QMainWindow):
    """
    View & Controller (MVC): Cria a UI e a conecta ao modelo de banco de dados.
    """
    def __init__(self, db_model):
        super().__init__()
        self.db = db_model
        self.setWindowTitle("Dashboard de Análise - Pontos MUST")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
        main_widget = QWidget()
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self._create_header()
        self._create_kpi_section()
        self._create_company_analysis_section()
        self._create_filters_section()
        self._create_details_table()
        
        self.main_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)
        scroll_area.setStyleSheet("border: none;")
        
        self.setCentralWidget(scroll_area)
        
        self._load_initial_data()

    def _create_header(self):
        header_layout = QVBoxLayout()
        title = QLabel("Dashboard de Análise de Pontos MUST")
        title.setObjectName("headerTitle")
        subtitle = QLabel("Visão geral das solicitações e ressalvas por empresa e ponto de conexão.")
        subtitle.setObjectName("headerSubtitle")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)

    def _create_kpi_section(self):
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        self.kpi_cards = {
            "unique_companies": self._create_kpi_card("Total de Empresas", "0"),
            "total_points": self._create_kpi_card("Total de Pontos de Conexão", "0"),
            "points_with_remarks": self._create_kpi_card("Pontos com Ressalvas", "0"),
            "percentage_with_remarks": self._create_kpi_card("% de Pontos com Ressalvas", "0.0%"),
        }
        for card in self.kpi_cards.values():
            self.kpi_layout.addWidget(card)
        self.main_layout.addLayout(self.kpi_layout)

    def _create_kpi_card(self, title_text, value_text):
        card = QFrame()
        card.setObjectName("kpiCard")
        card_layout = QVBoxLayout(card)
        title = QLabel(title_text)
        title.setObjectName("kpiTitle")
        value = QLabel(value_text)
        value.setObjectName("kpiValue")
        card_layout.addWidget(title)
        card_layout.addWidget(value)
        return card
        
    def _create_company_analysis_section(self):
        section_title = QLabel("Análise por Empresa")
        section_title.setObjectName("sectionTitle")
        self.main_layout.addWidget(section_title)
        self.company_analysis_layout = QGridLayout()
        self.company_analysis_layout.setSpacing(20)
        self.main_layout.addLayout(self.company_analysis_layout)

    def _create_company_card(self, company_name, stats):
        card = QFrame()
        card.setObjectName("kpiCard")
        layout = QVBoxLayout(card)
        name_label = QLabel(company_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        with_remarks = stats.get('with_remarks', 0)
        total = stats.get('total', 0)
        stats_text = f"Com Ressalvas: {with_remarks} / {total}"
        stats_label = QLabel(stats_text)
        stats_label.setObjectName("kpiTitle")
        layout.addWidget(name_label)
        layout.addWidget(stats_label)
        return card

    def _create_filters_section(self):
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        layout = QVBoxLayout(filter_frame)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        grid_layout.addWidget(QLabel("Empresa"), 0, 0)
        self.company_combo = QComboBox()
        grid_layout.addWidget(self.company_combo, 1, 0)
        
        grid_layout.addWidget(QLabel("Pesquisar"), 0, 1)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cód ONS, Ressalva...")
        grid_layout.addWidget(self.search_input, 1, 1)

        grid_layout.setColumnStretch(2, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.clear_button = QPushButton("Limpar")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self._clear_filters)
        
        self.filter_button = QPushButton("Filtrar")
        self.filter_button.setObjectName("filterButton")
        self.filter_button.clicked.connect(self._apply_filters)

        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.filter_button)

        layout.addLayout(grid_layout)
        layout.addLayout(button_layout)
        self.main_layout.addWidget(filter_frame)

    def _create_details_table(self):
        table_title = QLabel("Detalhes dos Pontos de Conexão")
        table_title.setObjectName("sectionTitle")
        self.main_layout.addWidget(table_title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Empresa", "Cód ONS", "Tensão (kV)", "Ressalva"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self._show_annotation_modal)
        self.main_layout.addWidget(self.table)

    def _load_initial_data(self):
        """Carrega todos os dados quando a aplicação inicia."""
        self._update_kpis()
        self._populate_company_analysis()
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
        row, col = 0, 0
        MAX_COLS = 3
        for company_stats in analysis_data:
            card = self._create_company_card(company_stats['nome_empresa'], company_stats)
            self.company_analysis_layout.addWidget(card, row, col)
            col += 1
            if col >= MAX_COLS:
                col = 0
                row += 1

    def _populate_filters(self):
        companies = ["Todas"] + self.db.get_unique_companies()
        self.company_combo.addItems(companies)

    def _populate_table(self, data):
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row_data['nome_empresa']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data['cod_ons']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row_data['tensao_kv'])))
            
            annotation = row_data.get('anotacao_geral')
            has_remark = annotation and str(annotation).strip().lower() not in ('nan', '')
            
            remark_item = QTableWidgetItem()
            if has_remark:
                remark_item.setText("Sim (Clique duplo)")
                remark_item.setForeground(Qt.GlobalColor.yellow)
                remark_item.setData(Qt.ItemDataRole.UserRole, annotation)
            else:
                remark_item.setText("Não")
            
            self.table.setItem(row_idx, 3, remark_item)
        self.table.resizeRowsToContents()

    def _apply_filters(self):
        """Lógica do Controller para aplicar filtros e atualizar a tabela."""
        filters = {
            "company": self.company_combo.currentText(),
            "search": self.search_input.text()
        }
        data = self.db.get_all_connection_points(filters)
        self._populate_table(data)
    
    def _clear_filters(self):
        self.company_combo.setCurrentIndex(0)
        self.search_input.clear()
        self._apply_filters()

    def _show_annotation_modal(self, model_index):
        """Mostra o modal com detalhes da anotação, se disponível."""
        if model_index.column() == 3:
            item = self.table.item(model_index.row(), 3)
            annotation_text = item.data(Qt.ItemDataRole.UserRole)
            if annotation_text:
                dialog = AnnotationDialog(str(annotation_text), self)
                dialog.exec()

# --- PARTE 3: PONTO DE ENTRADA DA APLICAÇÃO ---

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Define o caminho do banco de dados usando o caminho específico que você forneceu
    db_path = Path(r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\AUTOMACÕES ONS\arquivos\database\database_consolidado.db")
    
    try:
        # 1. Controller instancia o Model
        db_model = DashboardDB(db_path)
        
        # 2. Controller instancia a View (e passa o modelo para ela)
        window = DashboardApp(db_model)
        window.show()
        
        sys.exit(app.exec())
        
    except FileNotFoundError as e:
        # Tratamento de erro simples se o BD não for encontrado
        error_dialog = QDialog()
        error_dialog.setWindowTitle("Erro Crítico")
        layout = QVBoxLayout()
        label = QLabel(str(e))
        layout.addWidget(label)
        error_dialog.setLayout(layout)
        error_dialog.exec()
        sys.exit(1)
