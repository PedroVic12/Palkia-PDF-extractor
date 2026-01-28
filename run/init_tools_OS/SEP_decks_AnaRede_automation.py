#!/usr/bin/env python3
"""
Sistema de Automação para AnaREDE e Organon
Automação de simulação de redes elétricas com CLI interativa
"""

from dataclasses import dataclass
from pathlib import Path
import pyautogui
import os
import subprocess
import time
from gtts import gTTS
import threading
from typing import Optional, List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from rich.tree import Tree
import pygame

try:
    from win10toast import ToastNotifier
    WINDOWS = True
except ImportError:
    WINDOWS = False
    print("⚠️  win10toast não disponível (apenas Windows)")


console = Console()


@dataclass
class ProgramConfig:
    """Configuração de programas e caminhos"""
    nome: str
    executavel: str
    atalhos: Dict[str, str]


class MouseTracker:
    """Rastreador de posição do mouse em tempo real"""
    
    def __init__(self):
        self.tracking = False
        self.positions = []
        
    def start_tracking(self, duration: int = 10):
        """Inicia rastreamento por um período definido"""
        self.tracking = True
        console.print(f"\n[yellow]🖱️  Rastreamento ativado por {duration} segundos[/yellow]")
        console.print("[cyan]Pressione ESC para parar[/cyan]\n")
        
        start_time = time.time()
        
        try:
            while self.tracking and (time.time() - start_time) < duration:
                    
                x, y = pyautogui.position()
                timestamp = time.time() - start_time
                
                # Atualizar display
                console.print(f"\r[green]Posição: X={x:4d}, Y={y:4d}[/green] | Tempo: {timestamp:.1f}s", end="")
                
                self.positions.append((x, y, timestamp))
                time.sleep(0.1)
                
        except Exception as e:
            console.print(f"[red]Erro ao rastrear posição: {e}[/red]")
        finally:
            self.tracking = False
            console.print("\n\n[yellow]Rastreamento finalizado[/yellow]")
            self.show_summary()
    
    def show_summary(self):
        """Mostra resumo das posições capturadas"""
        if not self.positions:
            console.print("[red]Nenhuma posição capturada[/red]")
            return
        
        table = Table(title="📍 Posições Capturadas", box=box.ROUNDED)
        table.add_column("#", style="cyan", justify="right")
        table.add_column("X", style="green", justify="right")
        table.add_column("Y", style="green", justify="right")
        table.add_column("Tempo (s)", style="yellow", justify="right")
        
        for i, (x, y, t) in enumerate(self.positions[-10:], 1):  # últimas 10
            table.add_row(str(i), str(x), str(y), f"{t:.2f}")
        
        console.print(table)
        
    def capture_position(self, label: str = ""):
        """Captura posição atual com label"""
        x, y = pyautogui.position()
        console.print(f"[green]✓[/green] {label}: X={x}, Y={y}")
        return (x, y)


class Notificador:
    """Sistema de notificações"""
    
    def __init__(self):
        self.toaster = ToastNotifier() if WINDOWS else None
        pygame.mixer.init()
    
    def mostrar(self, titulo: str, mensagem: str, duracao: int = 5):
        """Mostra notificação do sistema"""
        if self.toaster:
            try:
                self.toaster.show_toast(
                    titulo, 
                    mensagem, 
                    duration=duracao,
                    threaded=True
                )
            except Exception as e:
                console.print(f"[yellow]⚠️  Notificação falhou: {e}[/yellow]")
        else:
            # Fallback para sistemas não-Windows
            console.print(Panel(f"[bold]{titulo}[/bold]\n{mensagem}", 
                              border_style="blue"))


class AssistenteFala:
    """Assistente de voz usando gTTS"""
    
    def __init__(self):
        self.enabled = True
        
    def falar(self, texto: str, mostrar: bool = True):
        """Gera e reproduz áudio"""
        if mostrar:
            console.print(f"[blue]🔊 {texto}[/blue]")
        
        if not self.enabled:
            return
            
        try:
            tts = gTTS(text=texto, lang='pt-br', slow=False)
            arquivo = "/tmp/fala_temp.mp3"
            tts.save(arquivo)
            
            # Reproduzir com pygame
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()
            
            # Aguardar finalizar
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            os.remove(arquivo)
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Erro ao gerar fala: {e}[/yellow]")
    
    def toggle(self):
        """Liga/desliga fala"""
        self.enabled = not self.enabled
        status = "ativada" if self.enabled else "desativada"
        console.print(f"[yellow]Fala {status}[/yellow]")


class EditCepelAutomation:
    """Automação específica para EditCepel"""
    
    ATALHOS = {
        'novo': 'ctrl+n',
        'abrir': 'ctrl+o',
        'regua': 'ctrl+*',
        'colar': 'ctrl+v',
        'salvar': 'ctrl+s',
        'fechar': 'ctrl+w'
    }
    
    def __init__(self, assistente: AssistenteFala):
        self.assistente = assistente
    
    def abrir_arquivo(self, caminho: str, delay: float = 2.0):
        """Abre arquivo PWF ou DAT no EditCepel"""
        self.assistente.falar("Abrindo arquivo no EditCepel")
        
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(delay)
        
        pyautogui.write(caminho, interval=0.05)
        time.sleep(0.5)
        
        pyautogui.press('enter')
        time.sleep(delay)
        
        console.print(f"[green]✓ Arquivo aberto: {Path(caminho).name}[/green]")
    
    def inserir_regua(self):
        """Insere régua de comandos"""
        self.assistente.falar("Inserindo régua de comandos")
        pyautogui.hotkey('ctrl', 'shift', '8')  # ctrl+*
        time.sleep(0.5)
        console.print("[green]✓ Régua inserida[/green]")
    
    def colar_deck_de_arquivo(self, caminho_arquivo: str, x_centro: int = 500, y_centro: int = 400):
        """Lê arquivo e cola conteúdo no editor"""
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Copiar para clipboard
            pyautogui.write('')  # limpar
            pyperclip.copy(conteudo)
            
            # Clicar no centro do editor
            pyautogui.click(x_centro, y_centro)
            time.sleep(0.3)
            
            # Colar
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            console.print(f"[green]✓ Deck colado: {Path(caminho_arquivo).name}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Erro ao colar deck: {e}[/red]")
    
    def mostrar_atalhos(self):
        """Exibe tabela de atalhos"""
        table = Table(title="⌨️  Atalhos EditCepel", box=box.ROUNDED)
        table.add_column("Ação", style="cyan")
        table.add_column("Atalho", style="yellow")
        
        for acao, atalho in self.ATALHOS.items():
            table.add_row(acao.title(), atalho)
        
        console.print(table)


class AnaRedeAutomation:
    """Automação para AnaREDE"""
    
    def __init__(self, assistente: AssistenteFala, notificador: Notificador):
        self.assistente = assistente
        self.notificador = notificador
        self.coordenadas = {
            'menu_caso': (50, 35),
            'abrir_caso': (100, 70),
            'menu_exibir': (106, 35),
            'menu_dados': (165, 35)
        }
    
    def abrir_programa(self, delay: float = 5.0):
        """Abre AnaREDE pelo menu iniciar"""
        self.assistente.falar("Abrindo AnaREDE versão 12")
        
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write('Anarede 12', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(delay)
        
        self.notificador.mostrar("AnaREDE", "Programa aberto com sucesso")
        console.print("[green]✓ AnaREDE aberto[/green]")
    
    def carregar_caso(self, caminho_sav: str):
        """Carrega arquivo .SAV"""
        self.assistente.falar("Carregando caso de fluxo de potência")
        
        # Clicar menu Caso
        pyautogui.click(*self.coordenadas['menu_caso'])
        time.sleep(1)
        
        # Clicar Abrir
        pyautogui.click(*self.coordenadas['abrir_caso'])
        time.sleep(2)
        
        # Digitar caminho
        pyautogui.write(caminho_sav, interval=0.05)
        pyautogui.press('enter')
        time.sleep(3)
        
        nome_caso = Path(caminho_sav).stem
        self.notificador.mostrar("Caso Carregado", f"Caso {nome_caso} pronto")
        console.print(f"[green]✓ Caso carregado: {nome_caso}[/green]")
    
    def executar_fluxo(self):
        """Executa cálculo de fluxo de potência"""
        self.assistente.falar("Executando cálculo de fluxo")
        
        # Pressionar F5 (atalho comum)
        pyautogui.press('f5')
        time.sleep(3)
        
        console.print("[green]✓ Fluxo executado[/green]")


class OrganonAutomation:
    """Automação para Organon"""
    
    def __init__(self, assistente: AssistenteFala, notificador: Notificador):
        self.assistente = assistente
        self.notificador = notificador
    
    def abrir_programa(self, delay: float = 5.0):
        """Abre Organon"""
        self.assistente.falar("Abrindo Organon")
        
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write('Organon', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(delay)
        
        console.print("[green]✓ Organon aberto[/green]")
    
    def carregar_diagrama(self, caminho_lst: str):
        """Carrega diagrama .lst"""
        self.assistente.falar("Carregando diagrama elétrico")
        
        # Menu Arquivo -> Abrir
        pyautogui.hotkey('ctrl', 'o')
        time.sleep(2)
        
        pyautogui.write(caminho_lst, interval=0.05)
        pyautogui.press('enter')
        time.sleep(3)
        
        nome_diagrama = Path(caminho_lst).stem
        self.notificador.mostrar("Diagrama", f"{nome_diagrama} carregado")
        console.print(f"[green]✓ Diagrama: {nome_diagrama}[/green]")


class FileExplorer:
    """Explorador de arquivos com Rich"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    def listar_diretorio(self, caminho: Optional[Path] = None) -> List[Path]:
        """Lista arquivos de um diretório"""
        if caminho is None:
            caminho = self.base_path
        
        try:
            items = sorted(caminho.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            return items
        except Exception as e:
            console.print(f"[red]Erro ao listar: {e}[/red]")
            return []
    
    def mostrar_tree(self, caminho: Optional[Path] = None, max_depth: int = 2):
        """Mostra árvore de diretórios"""
        if caminho is None:
            caminho = self.base_path
        
        tree = Tree(f"📁 [bold cyan]{caminho.name}[/bold cyan]")
        self._build_tree(tree, caminho, 0, max_depth)
        console.print(tree)
    
    def _build_tree(self, tree, path: Path, depth: int, max_depth: int):
        """Constrói árvore recursivamente"""
        if depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    branch = tree.add(f"📁 [cyan]{item.name}[/cyan]")
                    self._build_tree(branch, item, depth + 1, max_depth)
                else:
                    icon = self._get_file_icon(item.suffix)
                    tree.add(f"{icon} [green]{item.name}[/green]")
        except PermissionError:
            tree.add("[red]⛔ Acesso negado[/red]")
    
    def _get_file_icon(self, extensao: str) -> str:
        """Retorna ícone baseado na extensão"""
        icons = {
            '.py': '🐍',
            '.sav': '💾',
            '.lst': '📋',
            '.pwf': '⚡',
            '.dat': '📊',
            '.xlsx': '📈',
            '.csv': '📉'
        }
        return icons.get(extensao.lower(), '📄')
    
    def mostrar_tabela(self, caminho: Optional[Path] = None):
        """Mostra arquivos em tabela"""
        if caminho is None:
            caminho = self.base_path
        
        items = self.listar_diretorio(caminho)
        
        table = Table(title=f"📂 {caminho}", box=box.ROUNDED)
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Tipo", style="blue")
        table.add_column("Nome", style="green")
        table.add_column("Tamanho", style="yellow", justify="right")
        
        for i, item in enumerate(items, 1):
            tipo = "📁 DIR" if item.is_dir() else self._get_file_icon(item.suffix) + " FILE"
            nome = item.name
            
            if item.is_file():
                tamanho = self._format_size(item.stat().st_size)
            else:
                tamanho = "-"
            
            table.add_row(str(i), tipo, nome, tamanho)
        
        console.print(table)
        return items
    
    def _format_size(self, size: int) -> str:
        """Formata tamanho de arquivo"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class CLIInterativo:
    """Interface CLI interativa principal"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.assistente = AssistenteFala()
        self.notificador = Notificador()
        self.mouse_tracker = MouseTracker()
        self.explorer = FileExplorer(base_path)
        
        self.anarede = AnaRedeAutomation(self.assistente, self.notificador)
        self.organon = OrganonAutomation(self.assistente, self.notificador)
        self.editcepel = EditCepelAutomation(self.assistente)
        
        self.casos_selecionados = {
            'sav': None,
            'diagrama': None,
            'deck': None
        }
    
    def mostrar_banner(self):
        """Mostra banner inicial"""
        banner = """
        ╔═══════════════════════════════════════════╗
        ║   ⚡ AUTOMAÇÃO SEP - AnaREDE & Organon  ║
        ║   Sistema Elétrico de Potência - ONS     ║
        ╚═══════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold blue"))
    
    def menu_principal(self):
        """Menu principal"""
        while True:
            console.clear()
            self.mostrar_banner()
            
            menu = Table(box=box.ROUNDED)
            menu.add_column("Opção", style="cyan", justify="center")
            menu.add_column("Descrição", style="white")
            
            opcoes = [
                ("1", "📂 Explorar arquivos (Tree)"),
                ("2", "📋 Selecionar casos/diagramas"),
                ("3", "▶️  Executar automação AnaREDE"),
                ("4", "▶️  Executar automação Organon"),
                ("5", "⌨️  Atalhos EditCepel"),
                ("6", "🖱️  Rastrear posição do mouse"),
                ("7", "🔊 Toggle voz"),
                ("0", "🚪 Sair")
            ]
            
            for num, desc in opcoes:
                menu.add_row(num, desc)
            
            console.print(menu)
            
            escolha = Prompt.ask("\n[bold yellow]Escolha uma opção[/bold yellow]", 
                               choices=[o[0] for o in opcoes])
            
            if escolha == "1":
                self.explorar_arquivos()
            elif escolha == "2":
                self.selecionar_casos()
            elif escolha == "3":
                self.executar_anarede()
            elif escolha == "4":
                self.executar_organon()
            elif escolha == "5":
                self.editcepel.mostrar_atalhos()
                Prompt.ask("\n[dim]Pressione Enter para continuar[/dim]")
            elif escolha == "6":
                self.rastrear_mouse()
            elif escolha == "7":
                self.assistente.toggle()
            elif escolha == "0":
                if Confirm.ask("Deseja realmente sair?"):
                    console.print("[yellow]Até logo! ⚡[/yellow]")
                    break
    
    def explorar_arquivos(self):
        """Explora estrutura de arquivos"""
        console.clear()
        console.print("[bold cyan]📂 Estrutura de Diretórios[/bold cyan]\n")
        
        self.explorer.mostrar_tree(max_depth=3)
        
        if Confirm.ask("\nMostrar detalhes em tabela?"):
            console.print()
            self.explorer.mostrar_tabela()
        
        Prompt.ask("\n[dim]Pressione Enter para voltar[/dim]")
    
    def selecionar_casos(self):
        """Seleção interativa de casos"""
        console.clear()
        console.print("[bold cyan]📋 Seleção de Casos/Diagramas[/bold cyan]\n")
        
        # Diretórios padrão
        dirs = {
            'sav': Path(self.base_path) / 'Sav',
            'diagrama': Path(self.base_path) / 'diagramas',
            'deck': Path(self.base_path) / 'decks'
        }
        
        for tipo, dir_path in dirs.items():
            if not dir_path.exists():
                console.print(f"[yellow]⚠️  Diretório {tipo} não encontrado: {dir_path}[/yellow]")
                continue
            
            console.print(f"\n[cyan]═══ {tipo.upper()} ═══[/cyan]")
            items = self.explorer.mostrar_tabela(dir_path)
            
            if items:
                idx = Prompt.ask(
                    f"Selecione {tipo} (número) ou [dim]Enter para pular[/dim]",
                    default=""
                )
                
                if idx.isdigit():
                    idx = int(idx) - 1
                    if 0 <= idx < len(items):
                        self.casos_selecionados[tipo] = items[idx]
                        console.print(f"[green]✓ Selecionado: {items[idx].name}[/green]")
        
        # Mostrar resumo
        console.print("\n[bold]📊 Casos Selecionados:[/bold]")
        for tipo, arquivo in self.casos_selecionados.items():
            if arquivo:
                console.print(f"  {tipo}: [green]{arquivo.name}[/green]")
            else:
                console.print(f"  {tipo}: [dim]não selecionado[/dim]")
        
        Prompt.ask("\n[dim]Pressione Enter para voltar[/dim]")
    
    def executar_anarede(self):
        """Executa automação AnaREDE"""
        console.clear()
        console.print("[bold cyan]⚡ Executando Automação AnaREDE[/bold cyan]\n")
        
        if not self.casos_selecionados['sav']:
            console.print("[red]❌ Nenhum arquivo .SAV selecionado![/red]")
            Prompt.ask("[dim]Pressione Enter[/dim]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Iniciando...", total=3)
            
            progress.update(task, description="Abrindo AnaREDE...")
            self.anarede.abrir_programa()
            progress.advance(task)
            
            progress.update(task, description="Carregando caso...")
            self.anarede.carregar_caso(str(self.casos_selecionados['sav']))
            progress.advance(task)
            
            progress.update(task, description="Executando fluxo...")
            self.anarede.executar_fluxo()
            progress.advance(task)
        
        console.print("\n[green]✅ Automação concluída![/green]")
        Prompt.ask("[dim]Pressione Enter[/dim]")
    
    def executar_organon(self):
        """Executa automação Organon"""
        console.clear()
        console.print("[bold cyan]📊 Executando Automação Organon[/bold cyan]\n")
        
        if not self.casos_selecionados['diagrama']:
            console.print("[red]❌ Nenhum diagrama selecionado![/red]")
            Prompt.ask("[dim]Pressione Enter[/dim]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Iniciando...", total=2)
            
            progress.update(task, description="Abrindo Organon...")
            self.organon.abrir_programa()
            progress.advance(task)
            
            progress.update(task, description="Carregando diagrama...")
            self.organon.carregar_diagrama(str(self.casos_selecionados['diagrama']))
            progress.advance(task)
        
        console.print("\n[green]✅ Automação concluída![/green]")
        Prompt.ask("[dim]Pressione Enter[/dim]")
    
    def rastrear_mouse(self):
        """Interface de rastreamento do mouse"""
        console.clear()
        console.print("[bold cyan]🖱️  Rastreamento de Posição do Mouse[/bold cyan]\n")
        
        console.print("Opções:")
        console.print("  [1] Capturar posição atual")
        console.print("  [2] Rastreamento contínuo (10s)")
        console.print("  [0] Voltar\n")
        
        escolha = Prompt.ask("Escolha", choices=["1", "2", "0"])
        
        if escolha == "1":
            label = Prompt.ask("Label para a posição (ex: Menu Caso)")
            console.print("\n[yellow]Mova o mouse para a posição desejada...[/yellow]")
            time.sleep(3)
            self.mouse_tracker.capture_position(label)
            Prompt.ask("\n[dim]Pressione Enter[/dim]")
            
        elif escolha == "2":
            self.mouse_tracker.start_tracking(duration=10)
            Prompt.ask("\n[dim]Pressione Enter[/dim]")


def main():
    """Função principal"""
    # Caminho base (ajustar conforme necessário)
    BASE_PATH = r"C:\Users\pedrovictor.veras\OneDrive - Operador Nacional do Sistema Eletrico\Documentos\ESTAGIO_ONS_PVRV_2025\ONS + SIN + Tarefas PLC 2026\SIN"
    
    # Verificar se caminho existe
    if not Path(BASE_PATH).exists():
        console.print(f"[red]❌ Caminho não encontrado: {BASE_PATH}[/red]")
        console.print("[yellow]Ajuste o BASE_PATH no código[/yellow]")
        return
    
    # Iniciar CLI
    cli = CLIInterativo(BASE_PATH)
    cli.menu_principal()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print("\n[yellow]Programa interrompido pelo usuário[/yellow]\n\n [red]{e}[/red]")
    except Exception as e:
        console.print(f"\n[red]Erro fatal: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())