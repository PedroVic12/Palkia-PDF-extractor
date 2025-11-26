"""
CLI.py - Program Launcher with Rich TUI

A simple CLI launcher that displays a menu of Python programs to run.
Each program can have its own working directory, main script, and requirements.txt.

Programs are defined in a dict config. To add a new program, add an entry to PROGRAMS dict.

UI components are imported from run/CLI_MENU_UI.py.

Usage:
    python CLI.py
    # or via launcher scripts (run_cli.bat / run_cli.sh)

Environment variables (optional):
    PROJECTS_ROOT: base path for all projects (defaults to script dir)
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.style import Style
except ImportError:
    raise ImportError(
        "A biblioteca 'rich' é necessária. Instale com: pip install rich"
    )

console = Console()


# Import UI components from run/CLI_MENU_UI.py
try:
    sys.path.insert(0, str(Path(__file__).parent / "run"))
    from CLI_MENU_UI import CLIMenu
except ImportError as e:
    print(f"Erro: Não foi possível importar CLI_MENU_UI.py: {e}")
    print("Certifique-se de que o arquivo run/CLI_MENU_UI.py existe.")
    sys.exit(1)

# ============================================================================
# CONFIG: Programs Dictionary
# ============================================================================
# Each program entry:
# {
#     "name": Display name in menu,
#     "script": Main Python script to run (relative to work_dir),
#     "work_dir": Working directory (relative to PROJECTS_ROOT, or absolute),
#     "requirements": Path to requirements.txt (relative to work_dir, or None if not needed)
# }

PROJECTS_ROOT = Path(os.getenv("PROJECTS_ROOT", Path(__file__).parent))

PROGRAMS: Dict[str, Dict[str, str]] = {
    "desktop_dashboard": {
        "name": "Desktop Dashboard (SP Atividades)",
        "script": "desktop_Dashboard_app.py",
        "work_dir": "src/ScrapperPDF",
        "requirements": "requirements.txt",
    },
    "palkia_gui": {
        "name": "Palkia PDF Extractor GUI",
        "script": "Palkia_GUI.py",
        "work_dir": "src/ScrapperPDF",
        "requirements": "requirements.txt",
    },
    "moderno_template": {
        "name": "Moderno Desktop UI Template",
        "script": "moderno_desktop_ui_template.py",
        "work_dir": "src/SistemaControleGestaoONS_Desktop_MVC/Pyside6-Desktop-Template",
        "requirements": None,  # no requirements.txt needed
    },
    "glass_carousel": {
        "name": "Glass Cards & Carousel Demo",
        "script": "glass_carousel_app.py",
        "work_dir": "src/SistemaControleGestaoONS_Desktop_MVC/Pyside6-Desktop-Template",
        "requirements": None,
    },
    "tree_mvc": {
        "name": "Tree MVC App",
        "script": "tree_mvc_app.py",
        "work_dir": "src/SistemaControleGestaoONS_Desktop_MVC/Pyside6-Desktop-Template",
        "requirements": None,
    },
    "qt6_template": {
        "name": "Qt6 Desktop Template (Merged)",
        "script": "Qt6_desktop_template.py",
        "work_dir": "src/SistemaControleGestaoONS_Desktop_MVC",
        "requirements": "requirements.txt",
    },
    "organizador": {
        "name": "File Organizer",
        "script": "organizador_arquivos.py",
        "work_dir": ".",
        "requirements": None,
    },
}

# ============================================================================
# FUNCTIONS
# ============================================================================


def resolve_path(relative_or_absolute: str) -> Path:
    """Resolve a path relative to PROJECTS_ROOT or as absolute."""
    p = Path(relative_or_absolute)
    if p.is_absolute():
        return p
    return PROJECTS_ROOT / p


def display_header():
    """Display welcome header."""
    console.clear()
    console.print(
        Panel(
            "[bold cyan]🚀 Program Launcher CLI[/bold cyan]\n\n"
            f"[dim]Projects Root: {PROJECTS_ROOT}[/dim]",
            border_style="blue",
            padding=(1, 2),
        )
    )


def display_menu() -> str:
    """Display menu and get user choice."""
    programs_list: List[Tuple[str, str]] = [
        (key, prog["name"]) for key, prog in PROGRAMS.items()
    ]

    console.print("\n[bold]Available Programs:[/bold]\n")
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="yellow")
    table.add_column("Program", style="white")

    for i, (key, name) in enumerate(programs_list, 1):
        table.add_row(str(i), name)

    table.add_row(str(len(programs_list) + 1), "[red]Exit[/red]")
    console.print(table)

    choices = [str(i) for i in range(1, len(programs_list) + 2)]
    choice = Prompt.ask(
        "\n[bold]Select a program[/bold]", choices=choices, default="1"
    )

    if int(choice) == len(programs_list) + 1:
        return None

    selected_key = programs_list[int(choice) - 1][0]
    return selected_key


def install_requirements(work_dir: Path, requirements_file: str) -> bool:
    """Install requirements if requirements.txt exists."""
    req_path = work_dir / requirements_file
    if not req_path.exists():
        console.print(
            f"[yellow]⚠️  Requirements file not found: {req_path}[/yellow]"
        )
        return True  # continue anyway

    console.print(f"\n[cyan]📦 Installing requirements from {requirements_file}...[/cyan]")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_path)],
            cwd=str(work_dir),
            check=False,
        )
        if result.returncode == 0:
            console.print("[green]✓ Requirements installed successfully.[/green]")
            return True
        else:
            console.print("[red]✗ Failed to install requirements.[/red]")
            if not Confirm.ask("Continue anyway?", default=True):
                return False
            return True
    except Exception as e:
        console.print(f"[red]✗ Error installing requirements: {e}[/red]")
        return False


def run_program(program_key: str) -> bool:
    """Run the selected program."""
    program = PROGRAMS[program_key]
    work_dir = resolve_path(program["work_dir"])
    script = program["script"]
    script_path = work_dir / script

    console.print(f"\n[bold cyan]📂 Working Directory: {work_dir}[/bold cyan]")
    console.print(f"[bold cyan]📄 Script: {script}[/bold cyan]")

    # Verify script exists
    if not script_path.exists():
        console.print(f"[red]✗ Script not found: {script_path}[/red]")
        return False

    # Install requirements if specified
    requirements = program.get("requirements")
    if requirements:
        if not install_requirements(work_dir, requirements):
            return False

    # Run the program
    console.print(f"\n[bold green]▶️  Starting {program['name']}...[/bold green]\n")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(work_dir),
            check=False,
        )
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]✗ Error running program: {e}[/red]")
        return False


def main():
    """Main CLI loop."""
    while True:
        display_header()
        selected_key = display_menu()

        if selected_key is None:
            console.print(
                "\n[bold cyan]👋 Goodbye![/bold cyan]\n"
            )
            sys.exit(0)

        program = PROGRAMS[selected_key]
        console.print(
            f"\n[bold]Selected: {program['name']}[/bold]"
        )

        if run_program(selected_key):
            console.print(
                f"\n[green]✓ {program['name']} finished successfully.[/green]"
            )
        else:
            console.print(
                f"\n[red]✗ {program['name']} encountered an error or was interrupted.[/red]"
            )

        if not Confirm.ask("\n[bold]Run another program?[/bold]", default=True):
            console.print(
                "\n[bold cyan]👋 Goodbye![/bold cyan]\n"
            )
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(0)