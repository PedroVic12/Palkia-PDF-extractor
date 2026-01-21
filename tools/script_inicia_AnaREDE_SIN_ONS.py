import pyautogui
import os
import subprocess
import time
from gtts import gTTS
import random
#! pip install pyautogui google-generativeai pyttsx3 colorama 
# ===== CONFIGURAÇÕES =====
PROGRAMAS = ["Explorador de arquivos", "Anarede 12", "Organon.exe"]
# Caminho dos arquivos a carregar (ajuste conforme sua máquina)
CAMINHO_SAV = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\Sav\3Q2025_estudo_v1.SAV"
CAMINHO_SPT = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\diagramas\SIN.lst"


from win10toast import ToastNotifier

# Create a ToastNotifier object
toaster = ToastNotifier()

# Show a toast notification
toaster.show_toast(
    "My Notification Title",  # Title of the notification
    "This is the message of my toast notification.",  # Message content
    icon_path="path/to/your/icon.ico",  # Optional: path to an icon file
    duration=5,  # Duration in seconds for which the notification is displayed
    threaded=True  # Optional: run in a separate thread to avoid blocking
)

# You can also use a simple message without a title or icon:
# toaster.show_toast("Simple Message", "This is a basic notification.")

# ===== FUNÇÃO PARA FALAR =====
def falar(texto):
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
# ===== ABRIR PROGRAMA =====
def abrir_programa(nome_programa):
    """Abre o programa digitando no menu iniciar"""
    falar(f"Abrindo {nome_programa}")
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write(nome_programa)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(5)
    print(f"✅ {nome_programa} aberto.")
# ===== CARREGAR CASO NO ANAREDE =====
def carregar_save_case(caminho_arquivo):
    """Carrega um arquivo .SAV no AnaREDE"""
    falar("Carregando caso do fluxo de potência.")
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
# ===== CARREGAR DIAGRAMA NO ORGANON =====
def carregar_diagrama(caminho_arquivo):
    """Carrega um arquivo de diagrama no Organon"""
    falar("Carregando diagrama elétrico no Organon.")
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
def diagnosticar_posicao_mouse():
    """
    Mostra a posição atual do mouse e emite um alerta.
    """
    falar("Diagnóstico da posição do mouse ativado. Mova o mouse para o local desejado.")
    time.sleep(3)
    x, y = pyautogui.position()
    falar(f"Posição do mouse: X={x}, Y={y}")
    print(f"Posição do mouse: X={x}, Y={y}")
    # Alerta visual (opcional)
    pyautogui.alert(text=f'Posição do mouse: X={x}, Y={y}', title='Diagnóstico de Posição', button='OK')

    
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


