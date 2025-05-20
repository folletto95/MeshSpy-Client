#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"

echo "[INFO] Verifico dipendenze di sistema..."
if ! dpkg -s python3-venv &>/dev/null; then
  echo "[INFO] Installo python3-venv (richiede sudo)..."
  sudo apt update && sudo apt install -y python3-venv
fi

# Crea il virtualenv SE NON ESISTE
if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Creo virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "[INFO] Attivo virtual environment..."
source "$VENV_DIR/bin/activate"

echo "[INFO] Carico variabili da .env se esiste..."
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "[INFO] Installo dipendenze da requirements.txt..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "[INFO] Avvio client.py..."
python3 client.py "$@"
