from dataclasses import dataclass
import pyautogui
import os
import subprocess
import time
from gtts import gTTS
import random
#! pip install pyautogui google-generativeai pyttsx3 colorama 
import pygame
import os
import tempfile
import time
from win10toast import ToastNotifier




class Configuracoes:
    def __init__(self):
        caminho_sav: str = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\Sav\3Q2025_estudo_v1.SAV"
        caminho_spt: str = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\diagramas\SIN.lst"
        self.PROGRAMAS: list[str] = ["Explorador de arquivos", "Anarede 12", "Organon.exe"]

        self.arquivos_anaRede: dict[str, str] = {
            "caminho_sav": caminho_sav,
            "caminho_spt": caminho_spt,   
        }

        # Create a ToastNotifier object
        self.toaster: ToastNotifier = ToastNotifier()


    def showToast(self, title: str, message: str, icon_path: str = None, duration: int = 5, threaded: bool = True):
        """Mostra uma notificação na tela"""
        """argumentos:
        title: str = Título da notificação
        message: str = Mensagem da notificação
        icon_path: str = Caminho do ícone da notificação
        duration: int = Tempo de duração da notificação em segundos
        threaded: bool = Se True, a notificação é mostrada em um thread separado
        """
        if icon_path is None:
            icon_path = os.path.join(os.getcwd(), "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = None

        self.toaster.show_toast(title, message, icon_path, duration, threaded)

        # You can also use a simple message without a title or icon:
        # toaster.show_toast("Simple Message", "This is a basic notification.")


class AnaRedeDeckBuilder:
    def __init__(self,assistant: any):
        self.assistant = assistant
      
    # ===== CARREGAR CASO NO ANAREDE =====
    def carregar_save_case(self,caminho_arquivo):
        """Carrega um arquivo .SAV no AnaREDE"""
        self.assistant.falar("Carregando caso do fluxo de potência.")
        time.sleep(2)
        # Simulação de cliques (ajustar coordenadas conforme tela)
        pyautogui.click(x=100, y=50)       # menu principal (Arquivo)
        time.sleep(1)
        pyautogui.click(x=120, y=150)     # opção "Abrir Caso"
        time.sleep(2)
        # Digita o caminho do arquivo e pressiona Enter
        pyautogui.write(caminho_arquivo)
        pyautogui.press('enter')
        time.sleep(3)
        print(f"✅ Caso {os.path.basename(caminho_arquivo)} carregado no AnaREDE.")


    def abrirEditCepel(self):
        """Abre o menu Edit -> Cepel"""
        self.assistant.abrir_programa("EditCepel")



    # ===== CARREGAR DIAGRAMA NO ORGANON =====
    def carregar_diagrama(self, caminho_arquivo: str):
        """Carrega um arquivo de diagrama no Organon"""
        self.assistant.falar("Carregando diagrama elétrico no Organon.")
        time.sleep(2)
        pyautogui.click(x=100, y=50)       # menu principal
        time.sleep(1)
        pyautogui.click(x=130, y=180)      # opção "Abrir Diagrama"
        time.sleep(2)
        pyautogui.write(caminho_arquivo)
        pyautogui.press('enter')
        time.sleep(3)
        print(f"✅ Diagrama {os.path.basename(caminho_arquivo)} carregado no Organon.")

    # ===== NOVA FUNÇÃO PARA DIAGNOSTICAR POSIÇÃO DO MOUSE =====
    def diagnosticar_posicao_mouse(self):
        """
        Mostra a posição atual do mouse e emite um alerta.
        """
        self.assistant.falar("Diagnóstico da posição do mouse ativado. Mova o mouse para o local desejado.")
        time.sleep(3)
        x, y = pyautogui.position()
        self.assistant.falar(f"Posição do mouse: X={x}, Y={y}")
        print(f"Posição do mouse: X={x}, Y={y}")
        # Alerta visual (opcional)
        pyautogui.alert(text=f'Posição do mouse: X={x}, Y={y}', title='Diagnóstico de Posição', button='OK')


class C3POGeminiAssistant:
    def __init__(self):
        pass
    
    def generate_gemini_response(self, prompt: str):
        """Gera uma resposta usando o modelo Gemini"""
        pass
    
    def execute_sql_query(self, query: str):
        """Executa uma consulta SQL"""
        pass
    
    def display_data(self, data: list[dict]):
        """Exibe os dados em uma tabela"""
        pass


    # ===== FUNÇÃO PARA FALAR =====
    def falar(self, texto: str):
        """Gera e executa um áudio em português (voz sintética)"""
        try:
            print(f"[voz] {texto}")
            tts = gTTS(text=texto, lang='pt-br')
            nome_arquivo = os.path.join(os.getcwd(), "fala_temp.mp3")
            tts.save(nome_arquivo)
            subprocess.run(["mpg123", nome_arquivo], check=True)
            os.remove(nome_arquivo)
        except FileNotFoundError:
            print("⚠️ Erro: 'mpg123' não encontrado. Instale-o (ex: sudo apt-get install mpg123).")
        except Exception as e:
            print(f"Erro ao gerar fala: {e}")

    def texto_para_fala_com_notificacao(texto, idioma='pt-br'):
        # Configuração inicial do pygame mixer
        pygame.mixer.init()
        
        # Criar arquivo de áudio temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            arquivo_audio = tmp_file.name

    # ===== ABRIR PROGRAMA =====
    def abrir_programa(self, nome_programa):
        """Abre o programa digitando no menu iniciar"""
        self.falar(f"Abrindo programa {nome_programa}")
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write(nome_programa)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(5)
        print(f"✅ {nome_programa} aberto.")


    
# ===== EXECUÇÃO =====
def anaRedeScript():
    print("🟢 Iniciando script de automação AnaREDE...")
    abrir_programa("Anarede 12")
    carregar_save_case(CAMINHO_SAV)

def OrganonScript():
    print("🟢 Iniciando script de automação Organon...")
    abrir_programa("Organon")
    carregar_diagrama(CAMINHO_SPT)

# ===== ROTINA PRINCIPAL =====
def run_automation():
    falar("Iniciando rotina automática AnaREDE e Organon para análise do caso RSE.")

    anaRedeScript()

    falar("Rotina finalizada com sucesso.")
    print("✅ Automação concluída.")


