"""
Script de Organização de Diretórios
Usa 'rich' para uma interface de console agradável e 'pathlib' para
uma manipulação moderna de arquivos.
"""

import sys
import shutil
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# Importações da biblioteca Rich
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress
except ImportError:
    print("Erro: A biblioteca 'rich' não está instalada.")
    print("Por favor, instale com: pip install rich")
    sys.exit(1)

# Inicializa o console do Rich
console = Console()

def exibir_menu_principal() -> str:
    """Exibe o menu principal usando Rich Panel."""
    console.clear()
    console.print(Panel(
        "[bold cyan]Organizador de Arquivos 1.0[/bold cyan]\n\n"
        "[1] Selecionar um diretório para organizar\n"
        "[2] Sair\n",
        title="Menu Principal",
        border_style="blue",
        padding=(1, 2)
    ))
    
    escolha = Prompt.ask(
        "Escolha uma opção", 
        choices=["1", "2"], 
        default="1"
    )
    return escolha

def obter_diretorio_alvo() -> Path | None:
    """Pede ao usuário um caminho de diretório e o valida."""
    caminho_str = Prompt.ask("[bold yellow]Por favor, arraste e solte o diretório aqui ou digite o caminho[/bold yellow]")
    
    # Limpa o caminho (arrastar e soltar pode adicionar aspas)
    caminho_str = caminho_str.strip().strip("'\"")
    
    caminho = Path(caminho_str)
    
    if not caminho.exists():
        console.print(f"\n[bold red]Erro: O caminho não existe:[/bold red] {caminho}")
        return None
    if not caminho.is_dir():
        console.print(f"\n[bold red]Erro: O caminho não é um diretório:[/bold red] {caminho}")
        return None
        
    return caminho

def mapear_arquivos_por_extensao(diretorio: Path) -> Dict[str, List[Path]]:
    """
    Função (quase) pura que lê o diretório e mapeia os arquivos.
    Retorna um dicionário: {".txt": [file1.txt, file2.txt], ...}
    """
    console.print(f"\n[cyan]Mapeando arquivos em {diretorio.name}...[/cyan]")
    mapa_extensoes = defaultdict(list)
    try:
        for item in diretorio.iterdir():
            # Pula diretórios e o próprio script
            if item.is_dir() or item.name == Path(__file__).name:
                continue
                
            # Obtém a extensão (ex: ".txt", ".pdf")
            extensao = item.suffix.lower()
            if not extensao:
                extensao = ".sem_extensao"
                
            mapa_extensoes[extensao].append(item)
            
    except PermissionError:
        console.print(f"\n[bold red]Erro de Permissão:[/bold red] Não foi possível ler o diretório {diretorio}")
        return {}
        
    return mapa_extensoes

def mover_arquivos_para_pastas(diretorio_base: Path, mapa: Dict[str, List[Path]]):
    """
    Função impura (com efeitos colaterais) que cria as pastas e move os arquivos.
    """
    if not mapa:
        console.print("[yellow]Nenhum arquivo para organizar.[/yellow]")
        return

    console.print(f"\n[bold green]Iniciando organização...[/bold green]")
    total_arquivos = sum(len(files) for files in mapa.values())

    with Progress(console=console) as progress:
        task_geral = progress.add_task("[cyan]Organizando...", total=total_arquivos)

        for extensao, arquivos in mapa.items():
            # Define o nome da pasta (ex: "TXT_Arquivos")
            nome_pasta = f"{extensao[1:].upper()}_Arquivos"
            pasta_destino = diretorio_base / nome_pasta
            
            # Cria a pasta se ela não existir
            pasta_destino.mkdir(exist_ok=True)
            
            for arquivo in arquivos:
                try:
                    shutil.move(str(arquivo), str(pasta_destino / arquivo.name))
                    progress.update(task_geral, advance=1, description=f"Movendo [bold]{arquivo.name}[/bold]...")
                except Exception as e:
                    console.print(f"[red]Erro ao mover {arquivo.name}: {e}[/red]")

    console.print(f"\n[bold green]Organização concluída com sucesso![/bold green]")
    console.print(f"Foram movidos {total_arquivos} arquivos.")

def fluxo_principal_organizador():
    """Executa o fluxo completo de organização."""
    diretorio = obter_diretorio_alvo()
    if not diretorio:
        Prompt.ask("\nPressione Enter para voltar ao menu...")
        return

    mapa_arquivos = mapear_arquivos_por_extensao(diretorio)
    if not mapa_arquivos:
        Prompt.ask("\nPressione Enter para voltar ao menu...")
        return

    # Mostrar um resumo antes de mover
    console.print("\n[bold]Resumo da Organização:[/bold]")
    for extensao, arquivos in mapa_arquivos.items():
        console.print(f"  - [cyan]{extensao}[/cyan]: {len(arquivos)} arquivo(s) -> (Pasta: [yellow]{extensao[1:].upper()}_Arquivos[/yellow])")

    if not Confirm.ask(f"\nVocê confirma a organização de {diretorio.name}?", default=True):
        console.print("[red]Organização cancelada.[/red]")
        Prompt.ask("\nPressione Enter para voltar ao menu...")
        return

    mover_arquivos_para_pastas(diretorio, mapa_arquivos)
    Prompt.ask("\nPressione Enter para voltar ao menu...")

def main():
    """Loop principal do menu funcional."""
    while True:
        escolha = exibir_menu_principal()
        
        if escolha == "1":
            fluxo_principal_organizador()
        elif escolha == "2":
            console.print("[bold cyan]Até logo![/bold cyan]")
            sys.exit(0)

if __name__ == "__main__":
    main()
