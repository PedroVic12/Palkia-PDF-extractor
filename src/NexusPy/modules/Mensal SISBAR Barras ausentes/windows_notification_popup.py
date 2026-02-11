from gtts import gTTS
import pygame
from win10toast import ToastNotifier
import os
import tempfile
import time

#! pip install gtts pygame win10toast

def texto_para_fala_com_notificacao(texto, idioma='pt-br'):
    # Configuração inicial do pygame mixer
    pygame.mixer.init()
    
    # Criar arquivo de áudio temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
        arquivo_audio = tmp_file.name

    try:
        # Criação da instância do gTTS
        tts = gTTS(text=texto, lang=idioma)
        tts.save(arquivo_audio)

        # Configurar e mostrar notificação
        toaster = ToastNotifier()
        toaster.show_toast(
            "Texto para Fala",
            f"Reproduzindo: {texto}",
            icon_path=None,
            duration=5,
            threaded=True
        )

        # Reproduzir áudio com pygame
        pygame.mixer.music.load(arquivo_audio)
        pygame.mixer.music.play()

        # Aguardar até terminar a reprodução
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    finally:
        # Limpeza do arquivo temporário
        pygame.mixer.quit()
        if os.path.exists(arquivo_audio):
            os.unlink(arquivo_audio)

if __name__ == "__main__":
    texto = "Olá, como você está hoje?"
    texto_para_fala_com_notificacao(texto)