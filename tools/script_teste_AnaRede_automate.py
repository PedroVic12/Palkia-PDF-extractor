#!/usr/bin/env python3
"""
script_inicial_anaRede.py - Sistema Completo de Automação AnaREDE e Organon
Integrado com CLI Launcher usando Rich TUI

Autor: Pedro Victor
Versão: 2.1.0
Data: Janeiro 2026
"""

# ============================================================================
# IMPORTS (ORIGINAIS + EXTENSÕES, NADA REMOVIDO)
# ============================================================================

import sys
import os
import subprocess
import time
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import pyautogui
import pygame

try:
    from gtts import gTTS
except ImportError:
    print("⚠️  gtts não instalado. Função de voz desabilitada.")
    gTTS = None

try:
    from win10toast import ToastNotifier
    WINDOWS = True
except ImportError:
    WINDOWS = False
    print("⚠️  win10toast não disponível (apenas Windows)")

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.style import Style
    from rich import box
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.live import Live
except ImportError:
    raise ImportError(
        "A biblioteca 'rich' é necessária. Instale com: pip install rich"
    )

console = Console()





# ============================================================================
# CLASSE CONFIGURACOES (ORIGINAL + EXTENSÃO SUPORTE .SPT E .PWF)
# ============================================================================
class Configuracoes:
    """Configurações originais do sistema"""
    
    def __init__(self):
        # Caminhos originais
        caminho_sav: str = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\Sav\3Q2025_estudo_v1.SAV"
        caminho_spt: str = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\diagramas\SIN.spt"
        caminho_pwf: str = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\Casos - Cenarios - ONS - Real\SIN\pwf\caso_base.pwf"
        
        # NOVA VARIÁVEL - Caminho dos decks
        self.caminho_decks_anaRede: str = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\ONS + SIN + Tarefas PLC 2026\SIN"
        
        self.PROGRAMAS: list[str] = ["Explorador de arquivos", "Anarede 12", "Organon.exe"]
        
        self.arquivos_anaRede: dict[str, str] = {
            "caminho_sav": caminho_sav,
            "caminho_spt": caminho_spt,
            "caminho_pwf": caminho_pwf,
            "caminho_decks": self.caminho_decks_anaRede,
        }
        
        self.toaster: ToastNotifier = ToastNotifier() if WINDOWS else None


# ============================================================================
# CLASSE C3POGeminiAssistant (ORIGINAL INTACTO)
# ============================================================================
class C3POGeminiAssistant:
    """Assistente original C3PO com Gemini"""
    
    def __init__(self):
        pygame.mixer.init()
        self.voice_enabled = True
    
    def falar(self, texto: str):
        console.print(f"[blue]🔊 {texto}[/blue]")
        if not self.voice_enabled or not gTTS:
            return
        try:
            tts = gTTS(text=texto, lang='pt-br', slow=False)
            arquivo = os.path.join(os.getcwd(), "fala_temp.mp3")
            tts.save(arquivo)
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            os.remove(arquivo)
        except Exception:
            pass
    
    def abrir_programa(self, nome_programa):
        self.falar(f"Abrindo programa {nome_programa}")
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write(nome_programa)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(5)


# ============================================================================
# CLASSE AnaRedeDeckBuilder (EXTENSÃO PARA .SPT E .PWF)
# ============================================================================
class AnaRedeDeckBuilder:
    """Classe original para automação do AnaREDE"""
    
    def __init__(self, assistant: C3POGeminiAssistant):
        self.assistant = assistant
        self.coordenadas = {}

    def carregar_save_case(self, caminho_arquivo):
        self.assistant.falar("Carregando arquivo SAV no AnaREDE")
        pyautogui.write(str(caminho_arquivo))
        pyautogui.press('enter')
        time.sleep(2)

    def carregar_spt_diagrama(self, caminho_arquivo):
        self.assistant.falar("Carregando diagrama SPT no Organon")
        pyautogui.write(str(caminho_arquivo))
        pyautogui.press('enter')
        time.sleep(2)

    def carregar_pwf_fluxo(self, caminho_arquivo):
        self.assistant.falar("Carregando arquivo PWF no AnaREDE")
        pyautogui.write(str(caminho_arquivo))
        pyautogui.press('enter')
        time.sleep(2)


# ============================================================================
# CLASSE FileExplorer (EXTENSÃO PARA FILTRAR .SAV .SPT .PWF)
# ============================================================================
class FileExplorer:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    def listar_por_extensao(self, extensoes: List[str]) -> List[Path]:
        arquivos = []
        for root, _, files in os.walk(self.base_path):
            for f in files:
                if f.lower().endswith(tuple(extensoes)):
                    arquivos.append(Path(root) / f)
        return arquivos


# ============================================================================
# CLASSE CLIMenu (MEMÓRIA EXPLÍCITA DOS ARQUIVOS)
# ============================================================================
class CLIMenu:
    def __init__(self, config: Configuracoes, assistant: C3POGeminiAssistant):
        self.config = config
        self.assistant = assistant
        self.deck_builder = AnaRedeDeckBuilder(assistant)
        self.explorer = FileExplorer(config.caminho_decks_anaRede)
        
        # MEMÓRIA DOS ARQUIVOS USADOS NA AUTOMAÇÃO
        self.casos_selecionados = {
            'sav': None,
            'spt': None,
            'pwf': None
        }

    def selecionar_arquivos_sep(self):
        console.clear()
        console.print("[bold cyan]📂 Seleção de Arquivos SEP[/bold cyan]\n")

        savs = self.explorer.listar_por_extensao(['.sav'])
        spts = self.explorer.listar_por_extensao(['.spt'])
        pwfs = self.explorer.listar_por_extensao(['.pwf'])

        def escolher(lista, label):
            for i, f in enumerate(lista, 1):
                console.print(f"{i} - {f.name}")
            idx = Prompt.ask(f"Escolha {label}", default="")
            if idx.isdigit() and 1 <= int(idx) <= len(lista):
                return lista[int(idx)-1]
            return None

        self.casos_selecionados['sav'] = escolher(savs, "SAV")
        self.casos_selecionados['spt'] = escolher(spts, "SPT")
        self.casos_selecionados['pwf'] = escolher(pwfs, "PWF")

        console.print("\n[green]Arquivos carregados em memória:[/green]")
        for k, v in self.casos_selecionados.items():
            console.print(f"{k}: {v}")


# ============================================================================
# FUNÇÕES ORIGINAIS (EXTENSÃO SEM REMOVER NADA)
# ============================================================================

def run_automation(assistant: C3POGeminiAssistant, deck_builder: AnaRedeDeckBuilder,
                   casos: dict):
    assistant.falar("Iniciando automação completa AnaREDE")

    if casos.get('sav'):
        deck_builder.carregar_save_case(casos['sav'])
    if casos.get('spt'):
        deck_builder.carregar_spt_diagrama(casos['spt'])
    if casos.get('pwf'):
        deck_builder.carregar_pwf_fluxo(casos['pwf'])

    assistant.falar("Automação finalizada com sucesso")


# ============================================================================
# MAIN
# ============================================================================

def main():
    console.print("[bold green]Sistema SEP iniciado[/bold green]")
    config = Configuracoes()
    assistant = C3POGeminiAssistant()
    cli = CLIMenu(config, assistant)
    cli.selecionar_arquivos_sep()
    run_automation(assistant, cli.deck_builder, cli.casos_selecionados)


if __name__ == "__main__":
    main()
