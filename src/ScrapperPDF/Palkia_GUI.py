import sys
import os
import re
from io import StringIO
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QLabel, QLineEdit, QTextEdit,
    QGroupBox, QTabWidget, QTableView
)
from PySide6.QtCore import QThread, QObject, Signal, QAbstractTableModel, Qt
from PySide6.QtGui import QFont

# Tenta importar pandas. Se falhar, o programa pode rodar, mas a visualização da tabela não funcionará.
try:
    import pandas as pd
except ImportError:
    pd = None
    print("AVISO: A biblioteca 'pandas' não está instalada. A visualização de tabelas estará desativada.")

# Tenta importar o script run.py. Se falhar, mostra um erro claro.
try:
    import run as run_script
except ImportError as e:
    print(f"ERRO CRÍTICO: Não foi possível importar o arquivo 'run.py'. Verifique se ele está na mesma pasta. Detalhes: {e}")
    sys.exit(1)

APP_STYLES = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}
QMainWindow {
    background-color: #212121;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #444;
    border-radius: 8px;
    margin-top: 10px;
    padding: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 10px;
    color: #f0f0f0;
}
QPushButton {
    background-color: #3c3f41;
    color: #f0f0f0;
    border: 1px solid #555;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #4f5355;
}
QPushButton:pressed {
    background-color: #2a2d2f;
}
QPushButton#run_button {
    background-color: #007acc; /* Azul */
}
QPushButton#run_button:hover {
    background-color: #008ae6;
}
QLineEdit, QTextEdit {
    background-color: #3c3f41;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px;
    color: #f0f0f0;
}
QLabel {
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #444;
    border-top: 0px;
}
QTabBar::tab {
    background: #3c3f41;
    border: 1px solid #444;
    border-bottom: none;
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background: #2b2b2b;
    margin-bottom: 0px;
}
QTableView {
    gridline-color: #444;
}
QHeaderView::section {
    background-color: #3c3f41;
    padding: 4px;
    border: 1px solid #555;
    font-weight: bold;
}
"""

class PandasModel(QAbstractTableModel):
    """Modelo para exibir um DataFrame do pandas em uma QTableView."""
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

class Worker(QObject):
    """
    Worker para executar tarefas em uma thread separada.
    """
    progress = Signal(str)  # Sinal para enviar mensagens de log
    finished = Signal()     # Sinal emitido quando a tarefa termina com sucesso
    error = Signal(str)     # Sinal emitido em caso de erro

    def __init__(self, task_function, *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Executa a função alvo e captura sua saída de 'print'."""
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        try:
            self.progress.emit(f"▶️ Executando a função: {self.task_function.__name__}\n")
            
            # Chama a função importada (ex: run_extract_PDF_tables)
            self.task_function(*self.args, **self.kwargs)
            
            # Restaura a saída padrão
            sys.stdout = old_stdout
            
            # Captura tudo que foi "printado"
            output = redirected_output.getvalue()
            for line in output.splitlines():
                self.progress.emit(line)
            
            self.finished.emit()
            
        except Exception as e:
            # Garante que a saída padrão seja restaurada mesmo em caso de erro
            sys.stdout = old_stdout
            # Captura qualquer saída que tenha sido gerada antes do erro
            output = redirected_output.getvalue()
            for line in output.splitlines():
                self.progress.emit(line)
            
            # Emite o sinal de erro
            import traceback
            error_details = f"❌ Erro na execução da tarefa: {e}\n"
            error_details += "------------------\n"
            error_details += traceback.format_exc()
            error_details += "------------------"
            self.error.emit(error_details)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palkia - Extrator de PDF")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(APP_STYLES)

        # Widget Central e Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # --- Grupo de Configuração ---
        config_group = QGroupBox("Configuração de Entrada")
        config_layout = QVBoxLayout(config_group)

        # Seleção de Pasta
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Pasta de Entrada: (Nenhuma selecionada)")
        self.folder_button = QPushButton("Selecionar Pasta")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.folder_button)
        config_layout.addLayout(folder_layout)

        # Input de Intervalos
        intervals_layout = QVBoxLayout()
        intervals_label = QLabel("Intervalos de Páginas (separados por vírgula):")
        self.intervals_input = QLineEdit()
        self.intervals_input.setPlaceholderText('Ex: "8-16", "8-24", "7-10"')
        intervals_layout.addWidget(intervals_label)
        intervals_layout.addWidget(self.intervals_input)
        config_layout.addLayout(intervals_layout)

        main_layout.addWidget(config_group)

        # --- Grupo de Ações ---
        actions_group = QGroupBox("Ações de Extração")
        actions_layout = QHBoxLayout(actions_group)
        self.run_tables_button = QPushButton("Extrair Tabelas")
        self.run_tables_button.setObjectName("run_button")
        self.run_text_button = QPushButton("Extrair Anotações (Texto)")
        self.run_text_button.setObjectName("run_button")
        self.run_tables_button.clicked.connect(lambda: self.run_task("extract_tables"))
        self.run_text_button.clicked.connect(lambda: self.run_task("extract_text"))
        actions_layout.addWidget(self.run_tables_button)
        actions_layout.addWidget(self.run_text_button)
        main_layout.addWidget(actions_group)

        # --- Abas de Resultados (Log e Tabela) ---
        results_tabs = QTabWidget()
        main_layout.addWidget(results_tabs)

        # Tab de Log
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Courier New", 9))
        log_layout.addWidget(self.log_output)
        results_tabs.addTab(log_widget, "📝 Log de Execução")

        # Tab de Tabela
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.table_view = QTableView()
        table_layout.addWidget(self.table_view)
        results_tabs.addTab(table_widget, "📊 Resultado da Tabela")
        self.results_tabs = results_tabs

        self.input_folder = None
        self.current_task_info = {}
        self.thread = None
        self.worker = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta com os PDFs")
        if folder:
            self.input_folder = folder
            self.folder_label.setText(f"Pasta de Entrada: ...{os.path.basename(folder)}")

    def run_task(self, task_name):
        if not self.input_folder:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione uma pasta de entrada primeiro.")
            return

        intervals = self.intervals_input.text()
        if task_name == "extract_tables" and not intervals:
            QMessageBox.warning(self, "Aviso", "Por favor, forneça os intervalos de páginas para extrair tabelas.")
            return

        self.log_output.clear()
        self.set_buttons_enabled(False)
        self.table_view.setModel(None) # Limpa a visualização da tabela anterior

        # Armazena informações sobre a tarefa atual para uso posterior
        self.current_task_info = {
            "name": task_name,
            "input_folder": self.input_folder,
        }

        # --- INJEÇÃO DA VARIÁVEL GLOBAL ---
        # Modificamos a variável 'input_folder' dentro do módulo 'run' importado
        # Isso permite que as funções usem o caminho selecionado na GUI
        try:
            run_script.input_folder = self.input_folder
            self.log_output.append(f"INFO: Pasta de entrada definida para: {self.input_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Erro Crítico", f"Não foi possível definir a pasta de entrada no script 'run.py'. Erro: {e}")
            self.set_buttons_enabled(True)
            return

        # Prepara a função e os argumentos para a thread
        if task_name == "extract_tables":
            try:
                # Converte a string de intervalos ' "8-16", "8-24" ' em uma lista ['8-16', '8-24']
                intervals_list = [interval.strip().strip('"\'') for interval in intervals.split(',')]
                target_function = run_script.run_extract_PDF_tables
                args = (intervals_list, "folder")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Formato", f"Formato de intervalos inválido: {e}")
                self.set_buttons_enabled(True)
                return
        elif task_name == "extract_text":
            target_function = run_script.extract_text_from_must_tables
            args = ("folder",)
        else:
            self.set_buttons_enabled(True)
            return

        # Configura e inicia a thread
        self.thread = QThread()
        self.worker = Worker(target_function, *args)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.progress.connect(self.append_log)
        self.worker.error.connect(self.on_task_error)

        self.thread.start()

    def append_log(self, text):
        """Adiciona texto ao log, removendo códigos de cor ANSI."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        self.log_output.append(clean_text)

    def on_task_finished(self):
        self.append_log("\n✅ Tarefa concluída com sucesso!")
        self.display_results()
        self.cleanup_thread()

    def on_task_error(self, error_message):
        self.append_log(f"\n{error_message}")
        self.cleanup_thread()

    def display_results(self):
        """Verifica se há resultados (tabelas) para exibir."""
        task_name = self.current_task_info.get("name")
        if task_name != "extract_tables" or not pd:
            return

        input_folder = self.current_task_info.get("input_folder")
        output_folder = os.path.join(input_folder, "tabelas_extraidas")

        if not os.path.isdir(output_folder):
            self.append_log("AVISO: Pasta de resultados 'tabelas_extraidas' não encontrada.")
            return

        try:
            # Encontra o arquivo .xlsx mais recente na pasta de saída
            excel_files = [f for f in os.listdir(output_folder) if f.lower().endswith('.xlsx')]
            if not excel_files:
                self.append_log("AVISO: Nenhum arquivo Excel encontrado na pasta de resultados.")
                return

            latest_file = max(excel_files, key=lambda f: os.path.getmtime(os.path.join(output_folder, f)))
            file_path = os.path.join(output_folder, latest_file)
            
            self.append_log(f"\nCarregando resultado de: {latest_file}...")
            df = pd.read_excel(file_path)
            
            model = PandasModel(df)
            self.table_view.setModel(model)
            self.results_tabs.setCurrentIndex(1) # Muda para a aba da tabela
            self.append_log("✅ Tabela carregada com sucesso!")
        except Exception as e:
            self.append_log(f"❌ Erro ao carregar e exibir o arquivo Excel: {e}")

    def cleanup_thread(self):
        self.set_buttons_enabled(True)
        self.thread.quit()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.thread = None
        self.worker = None

    def set_buttons_enabled(self, enabled):
        self.run_tables_button.setEnabled(enabled)
        self.run_text_button.setEnabled(enabled)
        self.folder_button.setEnabled(enabled)

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Aviso", "Uma tarefa está em execução. Por favor, aguarde a conclusão.")
            event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())