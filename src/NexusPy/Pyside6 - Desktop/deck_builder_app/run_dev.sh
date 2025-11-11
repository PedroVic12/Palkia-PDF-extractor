#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to the script's directory
cd "$SCRIPT_DIR"

VENV_DIR="venv"

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "--- Criando ambiente virtual em '$VENV_DIR' ---"
    python -m venv "$VENV_DIR"
fi

echo "--- Ativando ambiente virtual ---"
source "$VENV_DIR/bin/activate"

echo "--- Verificando e instalando dependências ---"
pip install -r requirements.txt

echo ""
echo "--- Executando a Aplicação Deck Builder ---"
python main.py

# Deactivate the virtual environment after the app closes
deactivate
