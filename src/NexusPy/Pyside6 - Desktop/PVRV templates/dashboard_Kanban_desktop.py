"""
Dashboard de Atividades SP - ONS
Aplicação PySide6 com Flask Backend (MVC)
Autor: Sistema de Controle ONS
"""

import sys
import os
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QFileDialog, QTableWidget,
    QTableWidgetItem, QSplitter, QTabWidget, QTextEdit, QListWidget,
    QMessageBox, QHeaderView, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView


# ==================== MODELO (Model) ====================
class ActivityModel:
    """Modelo de dados para atividades"""
    
    def __init__(self):
        self.data: pd.DataFrame = pd.DataFrame()
        self.filtered_data: pd.DataFrame = pd.DataFrame()
        self.sheets: Dict[str, pd.DataFrame] = {}
        self.current_sheet = "Consolidado"
        self.filters = {
            'responsavel': 'Todos',
            'status': 'Todos',
            'ressalva': 'Todas'
        }
    
    def load_excel(self, filepath: str) -> bool:
        """Carrega arquivo Excel"""
        try:
            xls = pd.ExcelFile(filepath)
            self.sheets = {sheet: pd.read_excel(xls, sheet_name=sheet) 
                          for sheet in xls.sheet_names}
            
            # Consolidar todas as abas
            all_data = []
            for sheet_name, df in self.sheets.items():
                df['ORIGEM'] = sheet_name
                all_data.append(df)
            
            self.data = pd.concat(all_data, ignore_index=True)
            self.filtered_data = self.data.copy()
            return True
        except Exception as e:
            print(f"Erro ao carregar Excel: {e}")
            return False
    
    def apply_filters(self):
        """Aplica filtros aos dados"""
        df = self.data.copy()
        
        # Filtro de aba
        if self.current_sheet != "Consolidado":
            df = df[df['ORIGEM'] == self.current_sheet]
        
        # Filtro de responsável
        if self.filters['responsavel'] != 'Todos':
            df = df[df['RESPONSÁVEL'] == self.filters['responsavel']]
        
        # Filtro de status
        if self.filters['status'] != 'Todos':
            df = df[df['STATUS'] == self.filters['status']]
        
        # Filtro de ressalva
        if self.filters['ressalva'] == 'Com Ressalvas':
            df = df[df['OBSERVAÇÃO'].notna() & (df['OBSERVAÇÃO'] != '')]
        elif self.filters['ressalva'] == 'Sem Ressalvas':
            df = df[df['OBSERVAÇÃO'].isna() | (df['OBSERVAÇÃO'] == '')]
        
        self.filtered_data = df
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas dos dados filtrados"""
        if self.filtered_data.empty:
            return {}
        
        stats = {
            'total': len(self.filtered_data),
            'pendentes': len(self.filtered_data[self.filtered_data['STATUS'] == 'Pendente']),
            'concluidos': len(self.filtered_data[self.filtered_data['STATUS'] == 'Concluído']),
            'responsaveis': self.filtered_data['RESPONSÁVEL'].nunique(),
            'com_ressalvas': len(self.filtered_data[
                self.filtered_data['OBSERVAÇÃO'].notna() & 
                (self.filtered_data['OBSERVAÇÃO'] != '')
            ])
        }
        return stats
    
    def get_chart_data(self) -> Dict:
        """Retorna dados para gráficos"""
        if self.filtered_data.empty:
            return {}
        
        return {
            'status': self.filtered_data['STATUS'].value_counts().to_dict(),
            'responsaveis': self.filtered_data['RESPONSÁVEL'].value_counts().to_dict(),
            'ressalvas': {
                'Com Ressalvas': len(self.filtered_data[
                    self.filtered_data['OBSERVAÇÃO'].notna() & 
                    (self.filtered_data['OBSERVAÇÃO'] != '')
                ]),
                'Sem Ressalvas': len(self.filtered_data[
                    self.filtered_data['OBSERVAÇÃO'].isna() | 
                    (self.filtered_data['OBSERVAÇÃO'] == '')
                ])
            }
        }


# ==================== FLASK API (Controller) ====================
app = Flask(__name__)
CORS(app)

# Instância global do modelo
model = ActivityModel()

@app.route('/api/load', methods=['POST'])
def load_file():
    """Endpoint para carregar arquivo"""
    data = request.json
    filepath = data.get('filepath')
    
    if model.load_excel(filepath):
        return jsonify({'success': True, 'sheets': list(model.sheets.keys())})
    return jsonify({'success': False, 'error': 'Erro ao carregar arquivo'}), 400

@app.route('/api/filter', methods=['POST'])
def apply_filter():
    """Endpoint para aplicar filtros"""
    data = request.json
    
    if 'sheet' in data:
        model.current_sheet = data['sheet']
    if 'responsavel' in data:
        model.filters['responsavel'] = data['responsavel']
    if 'status' in data:
        model.filters['status'] = data['status']
    if 'ressalva' in data:
        model.filters['ressalva'] = data['ressalva']
    
    model.apply_filters()
    return jsonify({'success': True})

@app.route('/api/data', methods=['GET'])
def get_data():
    """Endpoint para obter dados filtrados"""
    if model.filtered_data.empty:
        return jsonify({'data': []})
    
    return jsonify({
        'data': model.filtered_data.fillna('').to_dict(orient='records')
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Endpoint para obter estatísticas"""
    return jsonify(model.get_statistics())

@app.route('/api/charts', methods=['GET'])
def get_charts():
    """Endpoint para dados de gráficos"""
    return jsonify(model.get_chart_data())

@app.route('/api/export', methods=['GET'])
def export_data():
    """Endpoint para exportar dados"""
    if model.filtered_data.empty:
        return jsonify({'error': 'Nenhum dado para exportar'}), 400
    
    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join('exports', filename)
    os.makedirs('exports', exist_ok=True)
    
    model.filtered_data.to_excel(filepath, index=False)
    return jsonify({'success': True, 'filepath': filepath})


# ==================== THREAD FLASK ====================
class FlaskThread(QThread):
    """Thread para rodar Flask em background"""
    
    def run(self):
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


# ==================== VIEW (PySide6) ====================
class DashboardWindow(QMainWindow):
    """Janela principal do Dashboard"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard de Atividades SP - ONS - PLC")
        self.setGeometry(100, 100, 1400, 900)
        
        self.current_file = None
        self.setup_ui()
        self.start_flask()
    
    def setup_ui(self):
        """Configura a interface"""
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        main_layout = QHBoxLayout(central)
        
        # Splitter para sidebar e conteúdo
        splitter = QSplitter(Qt.Horizontal)
        
        # ===== SIDEBAR =====
        sidebar = self.create_sidebar()
        splitter.addWidget(sidebar)
        
        # ===== CONTEÚDO PRINCIPAL =====
        content = self.create_content_area()
        splitter.addWidget(content)
        
        # Proporções do splitter
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
    
    def create_sidebar(self) -> QWidget:
        """Cria a barra lateral com controles"""
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.StyledPanel)
        sidebar.setMaximumWidth(300)
        
        layout = QVBoxLayout(sidebar)
        
        # Título
        title = QLabel("Controles")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Botão carregar arquivo
        self.btn_load = QPushButton("📁 Carregar Excel")
        self.btn_load.setMinimumHeight(40)
        self.btn_load.clicked.connect(self.load_file)
        layout.addWidget(self.btn_load)
        
        # Label do arquivo
        self.lbl_file = QLabel("Nenhum arquivo carregado")
        self.lbl_file.setWordWrap(True)
        self.lbl_file.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.lbl_file)
        
        # Botão exportar
        self.btn_export = QPushButton("💾 Exportar Dados")
        self.btn_export.setMinimumHeight(40)
        self.btn_export.clicked.connect(self.export_data)
        layout.addWidget(self.btn_export)
        
        # Separador
        layout.addWidget(QLabel("─" * 40))
        
        # Filtros
        filter_title = QLabel("Filtros")
        filter_title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(filter_title)
        
        # Seletor de aba
        layout.addWidget(QLabel("Visão por Aba:"))
        self.combo_sheet = QComboBox()
        self.combo_sheet.addItem("Consolidado")
        self.combo_sheet.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.combo_sheet)
        
        # Filtro responsável
        layout.addWidget(QLabel("Responsável:"))
        self.combo_responsavel = QComboBox()
        self.combo_responsavel.addItem("Todos")
        self.combo_responsavel.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.combo_responsavel)
        
        # Filtro status
        layout.addWidget(QLabel("Status Geral:"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Todos", "Pendente", "Concluído"])
        self.combo_status.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.combo_status)
        
        # Filtro ressalvas
        layout.addWidget(QLabel("Ressalvas:"))
        self.combo_ressalva = QComboBox()
        self.combo_ressalva.addItems(["Todas", "Com Ressalvas", "Sem Ressalvas"])
        self.combo_ressalva.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.combo_ressalva)
        
        layout.addStretch()
        
        return sidebar
    
    def create_content_area(self) -> QWidget:
        """Cria a área de conteúdo principal"""
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab Dashboard
        self.tab_dashboard = self.create_dashboard_tab()
        self.tabs.addTab(self.tab_dashboard, "📊 Dashboard")
        
        # Tab Kanban
        self.tab_kanban = self.create_kanban_tab()
        self.tabs.addTab(self.tab_kanban, "📋 Kanban")
        
        # Tab Tabela
        self.tab_table = self.create_table_tab()
        self.tabs.addTab(self.tab_table, "📄 Detalhes")
        
        layout.addWidget(self.tabs)
        
        return content
    
    def create_dashboard_tab(self) -> QWidget:
        """Cria a aba de dashboard com estatísticas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Cards de estatísticas
        cards_layout = QGridLayout()
        
        self.stat_cards = {}
        stats = [
            ("total", "Total Atividades", "#3498db"),
            ("pendentes", "Pendentes", "#e74c3c"),
            ("concluidos", "Concluídos", "#2ecc71"),
            ("responsaveis", "Responsáveis", "#f39c12")
        ]
        
        for i, (key, label, color) in enumerate(stats):
            card = self.create_stat_card(label, "0", color)
            self.stat_cards[key] = card
            cards_layout.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(cards_layout)
        
        # WebView para gráficos
        self.web_charts = QWebEngineView()
        self.web_charts.setMinimumHeight(400)
        layout.addWidget(self.web_charts)
        
        return tab
    
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Cria um card de estatística"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Arial", 10))
        
        value_lbl = QLabel(value)
        value_lbl.setFont(QFont("Arial", 24, QFont.Bold))
        value_lbl.setObjectName("value")
        
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        
        return card
    
    def create_kanban_tab(self) -> QWidget:
        """Cria a aba Kanban"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        self.kanban_columns = {}
        for status in ["Pendente", "Em Andamento", "Concluído"]:
            column = QListWidget()
            column.setStyleSheet("""
                QListWidget {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 5px;
                }
            """)
            self.kanban_columns[status] = column
            
            col_widget = QWidget()
            col_layout = QVBoxLayout(col_widget)
            col_layout.addWidget(QLabel(f"<b>{status}</b>"))
            col_layout.addWidget(column)
            
            layout.addWidget(col_widget)
        
        return tab
    
    def create_table_tab(self) -> QWidget:
        """Cria a aba de tabela de detalhes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.table)
        
        return tab
    
    def start_flask(self):
        """Inicia o servidor Flask em thread separada"""
        self.flask_thread = FlaskThread()
        self.flask_thread.start()
    
    def load_file(self):
        """Carrega arquivo Excel"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo Excel",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        
        if filepath:
            self.current_file = filepath
            self.lbl_file.setText(os.path.basename(filepath))
            
            # Chamar API para carregar
            import requests
            try:
                response = requests.post(
                    'http://127.0.0.1:5000/api/load',
                    json={'filepath': filepath}
                )
                if response.json().get('success'):
                    sheets = response.json().get('sheets', [])
                    self.combo_sheet.clear()
                    self.combo_sheet.addItem("Consolidado")
                    self.combo_sheet.addItems(sheets)
                    
                    self.update_data()
                    QMessageBox.information(self, "Sucesso", "Arquivo carregado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar arquivo: {e}")
    
    def apply_filters(self):
        """Aplica filtros via API"""
        if not self.current_file:
            return
        
        import requests
        try:
            requests.post(
                'http://127.0.0.1:5000/api/filter',
                json={
                    'sheet': self.combo_sheet.currentText(),
                    'responsavel': self.combo_responsavel.currentText(),
                    'status': self.combo_status.currentText(),
                    'ressalva': self.combo_ressalva.currentText()
                }
            )
            self.update_data()
        except Exception as e:
            print(f"Erro ao aplicar filtros: {e}")
    
    def update_data(self):
        """Atualiza dados na interface"""
        import requests
        
        try:
            # Atualizar estatísticas
            stats = requests.get('http://127.0.0.1:5000/api/statistics').json()
            for key, card in self.stat_cards.items():
                value_lbl = card.findChild(QLabel, "value")
                if value_lbl and key in stats:
                    value_lbl.setText(str(stats[key]))
            
            # Atualizar tabela
            data_response = requests.get('http://127.0.0.1:5000/api/data').json()
            data = data_response.get('data', [])
            
            if data:
                columns = list(data[0].keys())
                self.table.setColumnCount(len(columns))
                self.table.setHorizontalHeaderLabels(columns)
                self.table.setRowCount(len(data))
                
                for i, row in enumerate(data):
                    for j, col in enumerate(columns):
                        item = QTableWidgetItem(str(row.get(col, '')))
                        self.table.setItem(i, j, item)
                
                self.table.resizeColumnsToContents()
            
            # Atualizar gráficos (HTML simples)
            self.update_charts()
            
        except Exception as e:
            print(f"Erro ao atualizar dados: {e}")
    
    def update_charts(self):
        """Atualiza gráficos no WebView"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial; padding: 20px; }
                .chart-container { margin: 20px 0; }
                canvas { max-height: 300px; }
            </style>
        </head>
        <body>
            <h3>Gráficos serão carregados aqui</h3>
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
        </body>
        </html>
        """
        self.web_charts.setHtml(html)
    
    def export_data(self):
        """Exporta dados filtrados"""
        import requests
        
        try:
            response = requests.get('http://127.0.0.1:5000/api/export')
            if response.json().get('success'):
                filepath = response.json().get('filepath')
                QMessageBox.information(self, "Sucesso", f"Dados exportados para:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar: {e}")


# ==================== MAIN ====================
def main():
    """Função principal"""
    app_qt = QApplication(sys.argv)
    app_qt.setStyle('Fusion')
    
    window = DashboardWindow()
    window.show()
    
    sys.exit(app_qt.exec())


if __name__ == "__main__":
    main()