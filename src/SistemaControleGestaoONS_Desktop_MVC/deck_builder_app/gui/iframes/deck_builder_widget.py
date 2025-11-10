from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QTableWidget, QTableWidgetItem, QFileDialog, QLabel, QHeaderView,
    QMessageBox
)
from PySide6.QtCore import Slot

# Adjust path to import from the new 'core' directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.dbar_parser import parse_dbar_file
from core.pdf_generator import generate_deck_report

class DeckBuilderWidget(QWidget):
    def __init__(self, side_menu=None):
        super().__init__()
        
        self.parsed_data = None # To store the parsed data for PDF generation

        self.main_layout = QVBoxLayout(self)
        
        # --- Create Widgets ---
        self.status_label = QLabel("Carregue um arquivo de deck (.txt) para começar.")
        
        # Main layout with buttons
        top_layout = QHBoxLayout()
        self.load_button = QPushButton("Carregar Deck (.txt)")
        self.pdf_button = QPushButton("Gerar Relatório PDF")
        self.pdf_button.setEnabled(False) # Disabled until data is loaded
        top_layout.addWidget(self.load_button)
        top_layout.addWidget(self.pdf_button)
        
        # Table for parsed data
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Barra", "Pg (MW)", "Qg (MVAr)", "Pl (MW)", "Ql (MVAr)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # --- Add Widgets to Layout ---
        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.table)
        
        # --- Connect Signals ---
        self.load_button.clicked.connect(self.load_deck_file)
        self.pdf_button.clicked.connect(self.generate_report)

    @Slot()
    def load_deck_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Abrir Arquivo de Deck", 
            "", # Start directory
            "Text Files (*.txt)"
        )
        
        if file_path:
            self.status_label.setText(f"Processando arquivo: {os.path.basename(file_path)}...")
            self.parsed_data = parse_dbar_file(file_path)
            
            if self.parsed_data and self.parsed_data.get('bars'):
                self.populate_table(self.parsed_data['bars'])
                self.status_label.setText(f"Arquivo processado com sucesso. {len(self.parsed_data['bars'])} barras encontradas.")
                self.pdf_button.setEnabled(True)
            else:
                self.status_label.setText("Falha ao processar o arquivo. Verifique o formato.")
                self.pdf_button.setEnabled(False)
                self.parsed_data = None

    def populate_table(self, bar_data):
        self.table.setRowCount(len(bar_data))
        for row_idx, bar in enumerate(bar_data):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(bar['num'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{bar['pg']:.2f}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{bar['qg']:.2f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{bar['pl']:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{bar['ql']:.2f}"))

    @Slot()
    def generate_report(self):
        if not self.parsed_data:
            QMessageBox.warning(self, "Aviso", "Não há dados carregados para gerar um relatório.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório PDF",
            "relatorio_deck.pdf",
            "PDF Files (*.pdf)"
        )

        if save_path:
            self.status_label.setText("Gerando PDF...")
            success = generate_deck_report(self.parsed_data, save_path)
            if success:
                QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em:\n{save_path}")
                self.status_label.setText(f"Relatório salvo em: {save_path}")
            else:
                QMessageBox.critical(self, "Erro", "Falha ao gerar o PDF. Verifique se as dependências do WeasyPrint estão instaladas corretamente e consulte o terminal para mais detalhes.")
                self.status_label.setText("Falha ao gerar o PDF.")
