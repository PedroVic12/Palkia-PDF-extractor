@echo off
REM ============================================================================
REM run_cli.bat - Windows CLI Launcher
REM ============================================================================
REM Launches CLI.py from the repo root with optional .env configuration.
REM
REM Features:
REM - Automatically finds and changes to the repo root
REM - Optionally loads .env file for environment variables
REM - Sets UTF-8 code page for proper character display
REM - Launches CLI.py to display program menu
REM
REM Usage:
REM   run_cli.bat
REM
REM Optional .env file in repo root:
REM   PROJECTS_ROOT=C:\path\to\projects
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul

REM Get the directory where this script is located (repo root)
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM Load .env file if it exists
if exist ".env" (
    echo [INFO] Loading .env configuration...
    for /f "usebackq tokens=* eol=#" %%a in (".env") do (
        if not "%%a"=="" (
            set "%%a"
        )
    )
)

REM Verify Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Verify CLI.py exists
if not exist "CLI.py" (
    echo [ERROR] CLI.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

REM Verify rich is installed, install if missing
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required package 'rich'...
    python -m pip install rich >nul
)

REM Launch CLI.py
echo [INFO] Launching CLI...
python CLI.py

popd
endlocal
