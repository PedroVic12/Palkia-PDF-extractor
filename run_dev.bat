@echo off
pushd "%~dp0"
cd src\ScrapperPDF
IF EXIST requirements.txt (
    echo "Instalando dependências..."
    pip install -r requirements.txt
)
echo "Iniciando PLC_Controle_Gestao_desktop.py..."
python desktop_Dashboard_app.py
popd
