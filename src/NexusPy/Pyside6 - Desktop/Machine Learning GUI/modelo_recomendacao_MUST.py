import sys
import os
import pandas as pd
import numpy as np
import json
import requests
import asyncio
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QGridLayout, QLabel, QLineEdit, QPushButton, QTabWidget, 
                               QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QColor, QFont
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, f1_score
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random

# pip install PySide6 pandas scikit-learn matplotlib requests numpy

# script feito por gemini 2.5

# --- CONFIGURAÇÃO DE AMBIENTE (VARIÁVEIS CRÍTICAS) ---
# Substitua com sua chave real para ativar o chatbot Gemini
GEMINI_API_KEY = "" 
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
MODEL_ML_LLM = "gemini-2.5-flash-preview-09-2025"

# --- 1. MOCK DATA (Dados do ONS para Treinamento) ---
# Dados simulados com base nas atividades fornecidas pelo usuário
MOCK_DATA = {
    'ATIVIDADES': [
        "Recomendação de 2xBCs ligados em Cerquilho para Média e Pesada.",
        "Avaliar faixas de reativo do CS Estreito no Volume 9.",
        "Reavaliação da rede complementar-45965.",
        "Recomendar desinstalação de SEPs para rede alterada.",
        "Avaliação da perda dupla que causa sobrecarga na transformação 440/138 kV.",
        "Avaliação da PAR-NPT3-ARQ.",
        "Estudar impactos de RSUL em LTs recomendadas para desligamento para controle de tensão.",
        "Análise de colapso de tensão na malha de 500 kV do SE.",
        "Recomendação de ação para risco de subtensão na DIT CTEEP em perda dupla."
    ],
    'OBSERVAÇÃO': [
        "Conversar com o PAR para ver se eles já investigaram este problema.",
        "CS Estreito não tem influência sobre problema de colapso de tensão.",
        "Verificar: enviar solicitações de saída de equipamentos aos poucos ou no fim.",
        "TR Mogi Mirim 3, TRs Araraquara, UHE Ilha Solteira.",
        "Lucas já avaliou e a Entrada em operação do seccionamento de Fernão dias resolve.",
        "inclusão no relatório 500 kV.",
        "Verificar impactos em função de RSUL.",
        "Reavaliamção da rede complementar.",
        "Retirar o requisito de máx UG sincronizadas."
    ],
    # Variável alvo (Y): Classificação de Ação - SIMULACAO, REQUISITO, DESLIGAMENTO
    'ACAO_ALVO': [
        "DESLIGAMENTO", "REQUISITO", "AVALIACAO", "DESLIGAMENTO", "AVALIACAO", 
        "REQUISITO", "DESLIGAMENTO", "AVALIACAO", "REQUISITO"
    ]
}
df_ons = pd.DataFrame(MOCK_DATA)


# --- 2. CÓDIGO DA INFRAESTRUTURA ML (THREADS) ---

class MLWorker(QThread):
    """Thread para treinar o modelo e calcular a previsão sem travar a GUI."""
    finished = Signal(tuple)
    error = Signal(str)

    def __init__(self, df, vectorizer, classifier):
        super().__init__()
        self.df = df
        self.vectorizer = vectorizer
        self.classifier = classifier
        self.model = None
        self.metrics = None
        self.X_train_vectorized = None
        self.X_test_vectorized = None
        self.X_full_vectorized = None
        
    def run(self):
        try:
            # Separar X e Y
            X = self.df['ATIVIDADES']
            y = self.df['ACAO_ALVO']

            # 1. Vectorização (Feature Engineering)
            self.X_full_vectorized = self.vectorizer.fit_transform(X)
            
            # 2. Treinamento
            self.model = self.classifier.fit(self.X_full_vectorized, y)
            
            # 3. Previsão e Métricas (usando o próprio treino para fins de demonstração)
            y_pred = self.model.predict(self.X_full_vectorized)
            
            self.metrics = {
                'accuracy': accuracy_score(y, y_pred),
                'precision': precision_score(y, y_pred, average='weighted', zero_division=0),
                'f1_score': f1_score(y, y_pred, average='weighted', zero_division=0)
            }
            
            self.finished.emit((self.model, self.vectorizer, self.metrics))
            
        except Exception as e:
            self.error.emit(f"Erro no treinamento ML: {e}")

class GeminiWorker(QThread):
    """Thread para chamar a API do Gemini sem travar a GUI."""
    result = Signal(str)
    error = Signal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
        
    def run(self):
        if not GEMINI_API_KEY:
            self.error.emit("Chave GEMINI_API_KEY não configurada.")
            return

        # Tentativa com exponential backoff (simplificado para o exemplo)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "contents": [{"parts": [{"text": self.prompt}]}],
                    "systemInstruction": {
                        "parts": [{"text": "Você é um analista de Sistemas Elétricos de Potência (SEP) do ONS. Sua resposta deve ser concisa e técnica, focada em resolver o problema de contingência."}]
                    }
                }

                response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=20)
                response.raise_for_status() # Levanta HTTPError para códigos de erro (4xx ou 5xx)
                
                result = response.json()
                text = result.get('candidates')[0].get('content').get('parts')[0].get('text')
                self.result.emit(text)
                return

            except requests.exceptions.RequestException as e:
                import time
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    self.error.emit(f"Erro de Conexão Gemini (tentativa {attempt + 1}): {e}")
                
            except Exception as e:
                self.error.emit(f"Erro na resposta da API: {e}")
                return


# --- 3. COMPONENTES MATPLOTLIB ---

class MplCanvas(FigureCanvas):
    """Classe para integrar o Matplotlib na interface PySide6."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Configurações do Matplotlib para o tema Dark
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1e1e1e')
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout(pad=0.5)
        super(MplCanvas, self).__init__(self.fig)


# --- 4. APLICAÇÃO PRINCIPAL PYSIDE6 ---

class ONSMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ONS Control Tower - Analista SEP [Powered by PySide6/Gemini]")
        self.setGeometry(100, 100, 1200, 800)
        
        self.vectorizer = TfidfVectorizer()
        self.classifier = LogisticRegression(random_state=42)
        self.ml_model = None
        self.ml_vectorizer = None
        
        self.setup_ui()
        self.apply_dark_style()
        self.train_model() # Treina o modelo ao iniciar

    def apply_dark_style(self):
        """Aplica o estilo visual escuro (QSS) para a aplicação."""
        style = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        QTabWidget::pane {
            border: 1px solid #333333;
            background-color: #252526;
        }
        QTabBar::tab {
            background: #3c3c3c;
            color: #d4d4d4;
            padding: 10px;
            border: 1px solid #3c3c3c;
            border-bottom-color: #252526; /* same as pane color */
        }
        QTabBar::tab:selected {
            background: #252526;
            border-top: 2px solid #569cd6;
        }
        QLabel {
            color: #d4d4d4;
            font-size: 10pt;
        }
        QLineEdit, QTextEdit {
            background-color: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #569cd6;
            color: #ffffff;
            border: none;
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #60a9e7;
        }
        QTableWidget {
            background-color: #1e1e1e;
            color: #d4d4d4;
            gridline-color: #333333;
            border: 1px solid #333333;
        }
        QHeaderView::section {
            background-color: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #555555;
            padding: 5px;
        }
        """
        self.setStyleSheet(style)
        
    def setup_ui(self):
        """Configura a estrutura principal da aplicação com abas."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 1. Aba Dashboard
        dashboard_widget = self.create_dashboard_tab()
        self.tab_widget.addTab(dashboard_widget, "1. Dashboard Atividades MUST")
        
        # 2. Aba Análise ML
        analysis_widget = self.create_analysis_tab()
        self.tab_widget.addTab(analysis_widget, "2. Treinamento e Análise ML")
        
        # 3. Aba Chatbot/Recomendação
        chatbot_widget = self.create_chatbot_tab()
        self.tab_widget.addTab(chatbot_widget, "3. Chatbot/Recomendação (Gemini)")
        
    # --- 5. CRIAÇÃO DAS ABAS ---

    def create_dashboard_tab(self):
        """Cria a aba de visualização das atividades ONS (MUST)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Dados de Atividades MUST (Mock Data - 6 Colunas Críticas)")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        # Tabela de Dados
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels(['STATUS', 'ATIVIDADES', 'RESPONSÁVEL', 'PREVISÃO', 'DIAS ÚTEIS', 'OBSERVAÇÃO'])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setRowCount(len(df_ons))

        for i, row in df_ons.iterrows():
            self.data_table.setItem(i, 0, QTableWidgetItem(row['ACAO_ALVO'])) # Usando ACAO_ALVO como STATUS para visualização
            self.data_table.setItem(i, 1, QTableWidgetItem(row['ATIVIDADES']))
            self.data_table.setItem(i, 2, QTableWidgetItem(random.choice(['Carol', 'Lucas', 'Alexandre'])))
            self.data_table.setItem(i, 3, QTableWidgetItem(str(random.randint(10, 100)) + " dias"))
            self.data_table.setItem(i, 4, QTableWidgetItem(str(random.randint(1, 20))))
            self.data_table.setItem(i, 5, QTableWidgetItem(row['OBSERVAÇÃO']))
            
        layout.addWidget(self.data_table)

        # Botões de Ação (Geração de Documentos Futura)
        buttons_layout = QHBoxLayout()
        btn_deck = QPushButton("Gerar DECK AnaREDE (Futuro)")
        btn_pdf = QPushButton("Gerar Relatório PDF (Futuro)")
        
        btn_deck.setToolTip("Gera o deck de simulação (requer integração com AnaREDE/Organon).")
        btn_pdf.setToolTip("Gera o relatório em PDF com a análise de contingência.")
        
        buttons_layout.addWidget(btn_deck)
        buttons_layout.addWidget(btn_pdf)
        layout.addLayout(buttons_layout)
        
        return widget

    def create_analysis_tab(self):
        """Cria a aba de gráficos ML (Acurácia, Precisão, Score)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Métricas de Classificação do Modelo")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Labels para exibir os valores das métricas
        self.metric_labels = {}
        metrics_display_layout = QHBoxLayout()
        
        for metric in ['Acurácia', 'Precisão', 'F1-Score']:
            container = QVBoxLayout()
            label_title = QLabel(metric + ":")
            label_value = QLabel("Aguardando Treino...")
            label_value.setFont(QFont("Arial", 12, QFont.Bold))
            label_value.setObjectName(metric.lower().replace('-', '_')) # Nome de objeto único
            self.metric_labels[metric.lower().replace('-', '_')] = label_value
            container.addWidget(label_title)
            container.addWidget(label_value)
            metrics_display_layout.addLayout(container)
        
        layout.addLayout(metrics_display_layout)
        
        # Container para os gráficos
        self.chart_canvas = MplCanvas(self, width=10, height=5)
        layout.addWidget(self.chart_canvas)
        
        btn_retrain = QPushButton("Retreinar Modelo ML")
        btn_retrain.clicked.connect(self.train_model)
        layout.addWidget(btn_retrain)
        
        return widget
    
    def create_chatbot_tab(self):
        """Cria a aba do Chatbot para gerar texto de relatório."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 1. Área de Chat/Resposta
        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setText("Chatbot Gemini: Pronto para gerar relatórios e recomendações.")
        layout.addWidget(self.chat_output, 1)

        # 2. Área de Input e Recomendação
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("Atividade de Contingência:"), 0, 0)
        self.input_activity = QLineEdit()
        self.input_activity.setPlaceholderText("Ex: Avaliar faixas de reativo do CS Estreito")
        input_layout.addWidget(self.input_activity, 0, 1)
        
        btn_recommend = QPushButton("Gerar Recomendação ML")
        btn_recommend.clicked.connect(self.predict_recommendation)
        input_layout.addWidget(btn_recommend, 0, 2)
        
        input_layout.addWidget(QLabel("Relatório Gemini (Instrução):"), 1, 0)
        self.input_report_prompt = QLineEdit()
        self.input_report_prompt.setPlaceholderText("Ex: Escreva um resumo técnico sobre a análise")
        input_layout.addWidget(self.input_report_prompt, 1, 1)
        
        btn_generate_report = QPushButton("Gerar Relatório com Gemini LLM")
        btn_generate_report.clicked.connect(self.generate_report)
        input_layout.addWidget(btn_generate_report, 1, 2)
        
        layout.addLayout(input_layout)
        
        return widget

    # --- 6. MÉTODOS DE TREINAMENTO E ML ---
    
    def train_model(self):
        """Inicia o treinamento do modelo em uma thread separada."""
        self.chat_output.append("Iniciando treinamento ML... A GUI não será travada.")
        
        self.worker_thread = MLWorker(df_ons, self.vectorizer, self.classifier)
        self.worker_thread.finished.connect(self.on_ml_finished)
        self.worker_thread.error.connect(self.on_ml_error)
        self.worker_thread.start()
        
    def on_ml_finished(self, results):
        """Recebe os resultados do treinamento e atualiza a GUI."""
        self.ml_model, self.ml_vectorizer, metrics = results
        self.chat_output.append("✅ Treinamento ML concluído com sucesso!")
        
        # 1. Atualizar Labels
        for key, value in metrics.items():
            if key in self.metric_labels:
                self.metric_labels[key].setText(f"{value:.4f}")
                
        # 2. Atualizar Gráficos
        self.plot_metrics(metrics)
        
    def on_ml_error(self, error_message):
        """Trata erros no treinamento ML."""
        self.chat_output.append(f"🛑 Erro ML: {error_message}")
        
    def plot_metrics(self, metrics):
        """Plota as métricas (Acurácia, Precisão, F1-Score) em gráfico de barras."""
        ax = self.chart_canvas.axes
        ax.clear()
        
        labels = ['Acurácia', 'Precisão', 'F1-Score']
        values = [metrics['accuracy'], metrics['precision'], metrics['f1_score']]
        
        colors = ['#569cd6', '#4cc9f0', '#b5179e']
        
        ax.bar(labels, values, color=colors)
        ax.set_ylim(0, 1.0)
        ax.set_title('Métricas do Modelo de Classificação', color='white')
        
        # Adicionar rótulos de valor
        for i, v in enumerate(values):
            ax.text(i, v + 0.05, f'{v:.3f}', ha='center', color='white')
            
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        
        self.chart_canvas.draw()
        
    # --- 7. MÉTODOS DE RECOMENDAÇÃO E CHATBOT ---

    def predict_recommendation(self):
        """Usa o modelo ML para prever a categoria e recomendar a OBS."""
        if not self.ml_model or not self.ml_vectorizer:
            self.chat_output.append("🛑 Modelo ML não treinado. Clique em 'Retreinar Modelo ML'.")
            return
            
        activity = self.input_activity.text()
        if not activity:
            self.chat_output.append("Por favor, insira uma Atividade de Contingência.")
            return

        # 1. Previsão de Categoria (Classification)
        X_new = self.ml_vectorizer.transform([activity])
        predicted_category = self.ml_model.predict(X_new)[0]
        
        # 2. Recomendação (Nearest Neighbors - Simples)
        # Usa o TF-IDF e um modelo K-Nearest Neighbors para encontrar a OBS mais próxima
        from sklearn.neighbors import NearestNeighbors
        nn_model = NearestNeighbors(n_neighbors=1, metric='cosine')
        nn_model.fit(self.ml_vectorizer.transform(df_ons['ATIVIDADES']))
        
        distances, indices = nn_model.kneighbors(X_new)
        closest_index = indices[0][0]
        closest_obs = df_ons.iloc[closest_index]['OBSERVAÇÃO']
        
        self.chat_output.append(f"\n--- ANÁLISE DE CONTINGÊNCIA ---")
        self.chat_output.append(f"Atividade Inserida: {activity}")
        self.chat_output.append(f"Categoria Prevista (ML): {predicted_category}")
        self.chat_output.append(f"Recomendação de Próxima Ação (OBS mais próxima): {closest_obs}")
        self.chat_output.append("----------------------------")


    def generate_report(self):
        """Inicia a geração de texto via Gemini LLM em uma thread separada."""
        prompt = self.input_report_prompt.text()
        if not prompt:
            self.chat_output.append("Por favor, insira uma instrução para o relatório.")
            return
            
        if not GEMINI_API_KEY:
            self.chat_output.append("🛑 Chave GEMINI_API_KEY não configurada. Não é possível chamar o LLM.")
            return

        activity = self.input_activity.text()
        full_prompt = (
            f"Contexto ONS: A atividade a ser analisada é '{activity}'. "
            f"Instrução para Relatório: {prompt}. "
            "Gere uma resposta técnica, concisa e formatada para um relatório, usando o contexto de Sistemas Elétricos de Potência."
        )

        self.chat_output.append(f"\n🧠 Gerando texto de relatório com Gemini...")
        
        self.gemini_worker = GeminiWorker(full_prompt)
        self.gemini_worker.result.connect(self.on_gemini_result)
        self.gemini_worker.error.connect(self.on_gemini_error)
        self.gemini_worker.start()

    def on_gemini_result(self, text):
        """Recebe o resultado do LLM e exibe no chat."""
        self.chat_output.append("✅ Relatório Gemini (Resposta):")
        self.chat_output.append(text)

    def on_gemini_error(self, error_message):
        """Trata erros da API Gemini."""
        self.chat_output.append(f"🛑 Erro Gemini: {error_message}")


if __name__ == '__main__':
    # Define o estilo de cores do Matplotlib (para garantir a integração com o dark theme)
    plt.style.use('dark_background')
    
    # Executa a aplicação PySide6
    app = QApplication(sys.argv)
    window = ONSMonitorApp()
    window.show()
    sys.exit(app.exec())