import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

"""CLI Launcher for Multiple Python Projects"""

from CLI_script import CLIMenu, run_program


PROJECTS_ROOT = Path(os.getenv("PROJECTS_ROOT", Path(__file__).parent))

print(f"🔍 Using PROJECTS_ROOT: {PROJECTS_ROOT}")
print("\n\n\n🚀 Python Multi-Project CLI Launcher")
print(f"🐍 Python Executable: {sys.executable}\n")

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
        "script": "app_template_desktop.py",
        "work_dir": "src/NexusPy/Pyside6 - Desktop/pyside6_tab_app",
        "requirements": None,  # no requirements.txt needed
    },
    "organizador": {
        "name": "File Organizer",
        "script": "organizador_arquivos.py",
        "work_dir": ".",
        "requirements": None,
    },

    "switch_VBA_to_python": {
        "name": "Switch from VBA to Python Script",
        "script": "demo_automation.py",
        "work_dir": "modules/switch-from-vba-to-python-example-main",
        "requirements": "requirements.txt",
    },

    "ETL_perdas_duplas_desktop": {
        "name": "ETL Perdas Duplas Desktop App",
        "script": "main.py",
        "work_dir": "",
        "requirements": "requirements.txt",
    },

    "gerar_relatorio_ons": {
        "name": "Gerar Relatório ONS Automatizado",
        "script": "Relatorio_Word_automatizado.py",
        "work_dir": "src/BulbassaurQT6-ETL/Relatorio_PLC_Automate/scripts",
        "requirements": "requirements.txt",
    },

}



def main():
    """Main CLI loop."""
    menu = CLIMenu(PROGRAMS, PROJECTS_ROOT)

    while True:
        menu.display_header()
        selected_key = menu.display_menu()

        if selected_key is None:
            menu.display_goodbye()
            sys.exit(0)

        program = PROGRAMS[selected_key]
        menu.display_program_selected(program["name"])

        if run_program(PROGRAMS,PROJECTS_ROOT,selected_key, menu):
            menu.display_success_message(program["name"])
        else:
            menu.display_error_message(program["name"])

        if not menu.ask_run_another():
            menu.display_goodbye()
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        menu = CLIMenu(PROGRAMS, PROJECTS_ROOT)
        menu.display_interrupted()
        sys.exit(0)

