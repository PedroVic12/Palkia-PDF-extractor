#!/bin/bash
# ============================================================================
# run_cli.sh - Unix/Linux/macOS CLI Launcher
# ============================================================================
# Launches CLI.py from the repo root with optional .env configuration.
#
# Features:
# - Automatically finds and changes to the repo root
# - Optionally loads .env file for environment variables
# - Launches CLI.py to display program menu
#
# Usage:
#   chmod +x run_cli.sh
#   ./run_cli.sh
#
# Optional .env file in repo root:
#   PROJECTS_ROOT=/path/to/projects
# ============================================================================

set -e

# Get the directory where this script is located (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env file if it exists
if [ -f ".env" ]; then
    echo "[INFO] Loading .env configuration..."
    set -a
    source .env
    set +a
fi

# Verify Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed or not in PATH."
    exit 1
fi

# Determine which python command to use
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Verify CLI.py exists
if [ ! -f "CLI.py" ]; then
    echo "[ERROR] CLI.py not found in $SCRIPT_DIR"
    exit 1
fi

# Verify rich is installed, install if missing
if ! $PYTHON_CMD -c "import rich" 2>/dev/null; then
    echo "[INFO] Installing required package 'rich'..."
    $PYTHON_CMD -m pip install rich > /dev/null
fi

# Launch CLI.py
echo "[INFO] Launching CLI..."
$PYTHON_CMD CLI.py

