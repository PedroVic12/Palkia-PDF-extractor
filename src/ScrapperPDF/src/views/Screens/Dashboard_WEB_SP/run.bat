@echo off
echo Configurando ambiente virtual...

:: 1. Verifica se a pasta 'venv' existe
IF NOT EXIST "venv" (
    echo Criando ambiente virtual 'venv'...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo Falha ao criar ambiente virtual. Verifique se o Python 3 esta no PATH.
        pause
        exit /b %ERRORLEVEL%
    )
)

:: 2. Ativa o ambiente virtual
call "venv\Scripts\activate.bat"

:: 3. Garante que 'pip' e 'uv' estejam instalados/atualizados
echo Instalando/Atualizando 'uv' (instalador rapido)...
pip install -q -U pip uv

:: 4. Instala dependencias usando 'uv'
echo Instalando dependencias (Flask, pandas, openpyxl)...
uv pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Falha ao instalar dependencias com uv.
    pause
    exit /b %ERRORLEVEL%
)

echo Iniciando servidor Flask...
echo.
echo =======================================================
echo  Servidor rodando em http://127.0.0.1:5000
echo  Pressione CTRL+C na janela deste terminal para parar.
echo =======================================================
echo.

:: 5. Define as variaveis de ambiente do Flask e inicia o servidor
set FLASK_APP=main.py
set FLASK_ENV=development
flask run

echo Servidor parado.
pause

