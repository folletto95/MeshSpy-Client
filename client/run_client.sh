#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"

echo "[INFO] Verifico python3-venv..."
if ! dpkg -s python3-venv &>/dev/null; then
  echo "[INFO] Installo python3-venv (richiede sudo)..."
  sudo apt update
  sudo apt install -y python3-venv
fi

# Crea il virtual environment SE non esiste
if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Creo virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Verifica esistenza file activate
if [ ! -f "$VENV_DIR/bin/activate" ]; then
  echo "[ERRORE] Il virtual environment non è stato creato correttamente."
  exit 1
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
