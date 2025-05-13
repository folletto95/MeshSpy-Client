#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Creo virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "[INFO] Attivo virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[INFO] Installo dipendenze da requirements.txt..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[INFO] Avvio client.py..."
python3 client.py "$@"
