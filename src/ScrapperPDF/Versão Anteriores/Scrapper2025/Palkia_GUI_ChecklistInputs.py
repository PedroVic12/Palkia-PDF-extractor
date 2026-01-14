import sys
import os
import re
from io import StringIO
import subprocess # Para abrir PDFs localmente

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QLabel, QLineEdit, QTextEdit,
    QGroupBox, QTabWidget, QTableView, QCheckBox, QScrollArea
)
from PySide6.QtCore import QThread, QObject, Signal, QAbstractTableModel, Qt
from PySide6.QtGui import QFont
import pandas as pd


try:
    from ansi2html import Ansi2HTMLConverter
    ansi_converter = Ansi2HTMLConverter(dark_bg=True, scheme="xterm")
except ImportError:
    ansi_converter = None
    print("AVISO: 'ansi2html' não está instalado. Os logs não serão coloridos.")

# Tenta importar o script run.py principal coma  automação do ETL
try:
    import run as run_script
except ImportError as e:
    print(f"ERRO CRÍTICO: Não foi possível importar 'run.py'. Verifique se ele está na mesma pasta. Detalhes: {e}")
    sys.exit(1)

# Importa o CSS 
from styles import APP_STYLES

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
    def rowCount(self, parent=None): return self._data.shape[0]
    def columnCount(self, parent=None): return self._data.shape[1]
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal: return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical: return str(self._data.index[section])
        return None

class ExplanationWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Guia de Uso e Configuração", parent)
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }")

        self.layout().addWidget(QLabel("<b>1. Intervalos de Páginas:</b>"))
        self.layout().addWidget(QLabel("   - Deixe o campo vazio ou digite ' * ' para processar <b>todas as páginas</b> do PDF."))
        self.layout().addWidget(QLabel("   - Digite ' 8* ' para processar <b>da página 8 em diante</b>."))
        self.layout().addWidget(QLabel("   - Use o formato ' 8-16, 20-25 ' para intervalos de páginas específicos, separados por vírgula."))

        self.layout().addWidget(QLabel("<br><b>2. Extração de Tabelas MUST:</b>"))
        self.layout().addWidget(QLabel("   - Este aplicativo foi otimizado para extrair as tabelas de <b>1 a 7</b> dos documentos MUST, identificadas pelo título da tabela."))
        self.layout().addWidget(QLabel("   - Certifique-se de que os PDFs contêm essas tabelas para resultados precisos."))

class Worker(QObject):
    progress = Signal(str)
    finished = Signal()
    error = Signal(str)

    def __init__(self, task_function, *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            self.progress.emit(f"▶️ Executando a função: {self.task_function.__name__}\n")
            self.task_function(*self.args, **self.kwargs)
            sys.stdout = old_stdout
            output = redirected_output.getvalue()
            for line in output.splitlines():
                self.progress.emit(line)
            self.finished.emit()
        except Exception as e:
            sys.stdout = old_stdout
            output = redirected_output.getvalue()
            for line in output.splitlines(): self.progress.emit(line)
            import traceback
            error_details = f"❌ Erro na execução da tarefa: {e}\n{traceback.format_exc()}"
            self.error.emit(error_details)

class PalkiaWindowGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palkia - Extrator de PDF")
        self.setGeometry(100, 100, 900, 700) # Aumentei um pouco o tamanho
        self.setStyleSheet(APP_STYLES)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        config_group = QGroupBox("Configuração de Entrada")
        config_layout = QVBoxLayout(config_group)
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Pasta de Entrada: (Nenhuma selecionada)")
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.folder_button)
        config_layout.addLayout(folder_layout)
        
        # Área para listagem de PDFs com checkboxes e campos de intervalo
        pdf_selection_group = QGroupBox("Seleção de PDFs e Intervalos")
        pdf_selection_layout = QVBoxLayout(pdf_selection_group)
        self.pdf_list_scroll_area = QScrollArea()
        self.pdf_list_scroll_area.setWidgetResizable(True)
        self.pdf_list_container = QWidget()
        self.pdf_list_layout = QVBoxLayout(self.pdf_list_container)
        self.pdf_list_scroll_area.setWidget(self.pdf_list_container)
        pdf_selection_layout.addWidget(self.pdf_list_scroll_area)

        config_layout.addWidget(pdf_selection_group)
        main_layout.addWidget(config_group)
        
        self.explanation_widget = ExplanationWidget() # Instancia o novo widget de explicação
        main_layout.addWidget(self.explanation_widget) # Adiciona ao layout principal

        actions_group = QGroupBox("Ações de Extração e Pós-Processamento")
        actions_layout = QHBoxLayout(actions_group)
        self.run_tables_button = QPushButton("1) Extrair Tabelas MUST")
        self.run_tables_button.setObjectName("run_button")
        self.run_text_button = QPushButton("2) Extrair Anotações ")
        self.run_text_button.setObjectName("run_button")
        self.run_consolidate_button = QPushButton("3) Consolidar Resultados")
        self.run_consolidate_button.setObjectName("run_button")
        self.run_tables_button.clicked.connect(lambda: self.run_task("extract_tables"))
        self.run_text_button.clicked.connect(lambda: self.run_task("extract_text"))
        self.run_consolidate_button.clicked.connect(lambda: self.run_task("consolidate"))
        self.run_database_button = QPushButton("4) Carregar no Banco de Dados")
        self.run_database_button.setObjectName("run_button")
        self.run_database_button.clicked.connect(lambda: self.run_task("load_database"))
        actions_layout.addWidget(self.run_tables_button)
        actions_layout.addWidget(self.run_text_button)
        actions_layout.addWidget(self.run_consolidate_button)
        actions_layout.addWidget(self.run_database_button) # Adiciona o novo botão
        main_layout.addWidget(actions_group)

        results_tabs = QTabWidget()
        main_layout.addWidget(results_tabs)
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Courier New", 9))
        log_layout.addWidget(self.log_output)
        results_tabs.addTab(log_widget, "📝 Log de Execução")
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.table_view = QTableView()
        self.export_button = QPushButton("📤 Exportar Tabela para .xlsx")
        self.export_button.setObjectName("export_excel")
        self.export_button.clicked.connect(self.export_table)
        self.export_button.setEnabled(False)
        table_layout.addWidget(self.table_view)
        table_layout.addWidget(self.export_button)
        results_tabs.addTab(table_widget, "📊 Resultado da Tabela")

        self.results_tabs = results_tabs
        self.input_folder = None
        self.current_task_info = {}
        self.thread = None
        self.worker = None
        self.pdf_widgets = {} # Dicionário para armazenar {"nome_pdf": {"checkbox": obj, "interval_input": obj}}

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com os PDFs")
        if folder:
            self.input_folder = folder
            self.folder_label.setText(f"Pasta de Entrada: ...{os.path.basename(folder)}")
            self.log_output.clear()
            self.append_log(f"Pasta selecionada: {folder}\n")
            self.populate_pdf_list(folder) # Popula a nova área de listagem de PDFs
    def populate_pdf_list(self, folder):
        # Limpa o layout anterior
        for i in reversed(range(self.pdf_list_layout.count())):
            widget = self.pdf_list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        self.pdf_widgets = {}
        pdf_files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.pdf')])

        if not pdf_files:
            no_pdf_label = QLabel("Nenhum arquivo PDF encontrado nesta pasta.")
            self.pdf_list_layout.addWidget(no_pdf_label)
            return

        for pdf_file in pdf_files:
            pdf_h_layout = QHBoxLayout()
            checkbox = QCheckBox(pdf_file)
            checkbox.setChecked(True) # Por padrão, todos os PDFs são selecionados
            interval_input = QLineEdit()
            interval_input.setPlaceholderText('Ex: "8-16", "8-24"')
            
            # Armazena os widgets para acesso futuro
            self.pdf_widgets[pdf_file] = {"checkbox": checkbox, "interval_input": interval_input}
            self.pdf_list_layout.addLayout(pdf_h_layout)

        self.pdf_list_layout.addStretch(1) # Para empurrar os itens para o topo

    def populate_pdf_list(self, folder):
        # Limpa o layout anterior
        for i in reversed(range(self.pdf_list_layout.count())):
            widget = self.pdf_list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        self.pdf_widgets = {}
        pdf_files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.pdf')])

        if not pdf_files:
            no_pdf_label = QLabel("Nenhum arquivo PDF encontrado nesta pasta.")
            self.pdf_list_layout.addWidget(no_pdf_label)
            return

        for pdf_file in pdf_files:
            pdf_h_layout = QHBoxLayout()
            checkbox = QCheckBox(pdf_file)
            checkbox.setChecked(True) # Por padrão, todos os PDFs são selecionados
            interval_input = QLineEdit()
            interval_input.setPlaceholderText('Ex: "8-16", "8-24"')
            
            # Armazena os widgets para acesso futuro
            self.pdf_widgets[pdf_file] = {"checkbox": checkbox, "interval_input": interval_input}
            pdf_h_layout.addWidget(checkbox)
            pdf_h_layout.addWidget(interval_input)
            
            # Adicionar um botão para abrir o PDF
            open_pdf_button = QPushButton("Abrir")
            open_pdf_button.clicked.connect(lambda _, file=pdf_file: self.open_pdf_local(file))
            pdf_h_layout.addWidget(open_pdf_button)

            self.pdf_list_layout.addLayout(pdf_h_layout)

        self.pdf_list_layout.addStretch(1) # Para empurrar os itens para o topo

    def open_pdf_local(self, pdf_name):
        if not self.input_folder:
            QMessageBox.warning(self, "Aviso", "Selecione uma pasta de entrada primeiro.")
            return

        pdf_path = os.path.join(self.input_folder, pdf_name)
        if not os.path.exists(pdf_path):
            QMessageBox.critical(self, "Erro", f"Arquivo PDF não encontrado: {pdf_path}")
            return

        try:
            if sys.platform == "win32":
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", pdf_path])
            else:
                subprocess.call(["xdg-open", pdf_path])
            self.append_log(f"<font color=\"#9CCC65\">Abrindo PDF: {pdf_name}</font>")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o PDF {pdf_name}: {e}")


    def run_task(self, task_name):
        if not self.input_folder:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta de entrada primeiro.")
            return
        self.log_output.clear()
        self.set_buttons_enabled(False)
        self.table_view.setModel(None)
        self.export_button.setEnabled(False)
        self.current_task_info = {"name": task_name, "input_folder": self.input_folder}
        try:
            run_script.input_folder = self.input_folder
            self.append_log(f"INFO: Pasta de entrada definida para: {self.input_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", f"Não foi possível definir a pasta no script 'run.py'. Erro: {e}")
            self.set_buttons_enabled(True)
            return
        if task_name == "extract_tables":
            try:
                intervals_list_for_run = []
                selected_pdf_files = []
                for pdf_file, widgets in self.pdf_widgets.items():
                    if widgets["checkbox"].isChecked():
                        interval = widgets["interval_input"].text().strip()
                        if not interval:
                            QMessageBox.warning(self, "Aviso", f"Por favor, forneça os intervalos de páginas para o PDF selecionado: {pdf_file}")
                            self.set_buttons_enabled(True)
                            return
                        selected_pdf_files.append(pdf_file)
                        intervals_list_for_run.append(interval)

                if not selected_pdf_files:
                    QMessageBox.warning(self, "Aviso", "Por favor, selecione pelo menos um PDF para extrair tabelas.")
                    self.set_buttons_enabled(True)
                    return

                # Atualiza run_script.pdf_files e run_script.intervalos_paginas com os valores selecionados
                # Supondo que run_script.run_extract_PDF_tables pode aceitar uma lista de arquivos e uma lista de intervalos
                # Pode ser necessário ajustar run.py para aceitar esses novos parâmetros.
                run_script.pdf_files_to_process = selected_pdf_files # Novo atributo para run.py
                run_script.intervalos_paginas_to_process = intervals_list_for_run # Novo atributo para run.py

                target_function = run_script.run_extract_PDF_tables
                args = (run_script.pdf_files_to_process, run_script.intervalos_paginas_to_process, "folder") # Passa a lista de arquivos e intervalos
            except Exception as e:
                QMessageBox.critical(self, "Erro de Formato", f"Formato de intervalos inválido ou erro ao preparar a lista: {e}")
                self.set_buttons_enabled(True)
                return
        elif task_name == "extract_text":
            # Adaptação para extract_text_from_must_tables
            selected_pdf_files = []
            for pdf_file, widgets in self.pdf_widgets.items():
                if widgets["checkbox"].isChecked():
                    selected_pdf_files.append(pdf_file)
            
            if not selected_pdf_files:
                QMessageBox.warning(self, "Aviso", "Por favor, selecione pelo menos um PDF para extrair anotações.")
                self.set_buttons_enabled(True)
                return
            
            run_script.pdf_files_to_process = selected_pdf_files
            target_function = run_script.extract_text_from_must_tables
            args = (run_script.pdf_files_to_process, "folder",)
        elif task_name == "consolidate":
            if hasattr(run_script, 'consolidate_and_merge_results'):
                target_function = run_script.consolidate_and_merge_results
                args = (self.input_folder,)
            else:
                QMessageBox.critical(self, "Erro", "A função 'consolidate_and_merge_results' não foi encontrada em 'run.py'.")
                self.set_buttons_enabled(True)
                return
        elif task_name == "load_database":
            if hasattr(run_script, 'run_database_load_process'):
                target_function = run_script.run_database_load_process
                args = (self.input_folder,)
            else:
                QMessageBox.critical(self, "Erro", "A função 'run_database_load_process' não foi encontrada em 'run.py'.")
                self.set_buttons_enabled(True)
                return
        else:
            self.set_buttons_enabled(True)
            return
        self.thread = QThread()
        self.worker = Worker(target_function, *args)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.progress.connect(self.append_log)
        self.worker.error.connect(self.on_task_error)
        self.thread.start()

    def append_log(self, text):
        if text.startswith('<font'):
            self.log_output.append(text)
            return
        if ansi_converter:
            html_text = ansi_converter.convert(text, full=False)
            self.log_output.append(html_text)
        else:
            clean_text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)
            self.log_output.append(clean_text)

    def on_task_finished(self):
        self.append_log("\n✅ Tarefa concluída com sucesso!")
        self.display_results()
        self.cleanup_thread()

    def on_task_error(self, error_message):
        self.append_log(f"\n{error_message}")
        self.cleanup_thread()

    def display_results(self):
        task_name = self.current_task_info.get("name")
        input_folder = self.current_task_info.get("input_folder")
        if not pd: return
        df_to_display = None
        if task_name == "extract_tables":
            df_to_display = self.load_latest_excel(os.path.join(input_folder, "tabelas_extraidas"))
        elif task_name == "extract_text":
            df_to_display = self.consolidate_and_load_excel(os.path.join(input_folder, "anotacoes_extraidas"))
        elif task_name == "consolidate":
            final_excel_path = os.path.join(input_folder, "database", "must_tables_PDF_notes_merged.xlsx")
            if os.path.exists(final_excel_path):
                df_to_display = pd.read_excel(final_excel_path)
        if df_to_display is not None and not df_to_display.empty:
            model = PandasModel(df_to_display)
            self.table_view.setModel(model)
            self.results_tabs.setCurrentIndex(1)
            self.export_button.setEnabled(True)
            self.append_log("✅ Tabela carregada com sucesso!")
        else:
            self.append_log("ℹ️ Nenhuma tabela para exibir.")

    def load_latest_excel(self, output_folder):
        latest_file_path = self.find_latest_file(output_folder, '.xlsx')
        if not latest_file_path: return None
        try:
            self.append_log(f"\nCarregando resultado de: {os.path.basename(latest_file_path)}...")
            return pd.read_excel(latest_file_path)
        except Exception as e:
            self.append_log(f"❌ Erro ao carregar o arquivo Excel: {e}")
            return None

    def consolidate_and_load_excel(self, output_folder):
        self.append_log("\nIniciando consolidação...")
        if not os.path.isdir(output_folder): return None
        try:
            all_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.lower().endswith('.xlsx')]
            if not all_files:
                self.append_log("AVISO: Nenhum arquivo de anotações (.xlsx) encontrado para consolidar.")
                return None
            df_list = [pd.read_excel(f) for f in all_files]
            consolidated_df = pd.concat(df_list, ignore_index=True)
            self.append_log(f"✅ Consolidação concluída. Total de {consolidated_df.shape[0]} registros.")
            return consolidated_df
        except Exception as e:
            self.append_log(f"❌ Erro durante a consolidação: {e}")
            return None

    def find_latest_file(self, folder, extension):
        if not os.path.isdir(folder): return None
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(extension)]
        if not files: return None
        return max(files, key=os.path.getmtime)

    def export_table(self):
        model = self.table_view.model()
        if not model or not isinstance(model, PandasModel):
            QMessageBox.warning(self, "Aviso", "Nenhuma tabela para exportar.")
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
        self.run_tables_button.setEnabled(enabled)
        self.run_text_button.setEnabled(enabled)
        self.run_consolidate_button.setEnabled(enabled)
        self.folder_button.setEnabled(enabled)

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Aviso", "Uma tarefa está em execução.")
            event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PalkiaWindowGUI()
    window.show()
    sys.exit(app.exec())