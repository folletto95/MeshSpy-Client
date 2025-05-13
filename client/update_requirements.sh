#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "[ERRORE] Virtual environment non trovato. Esegui prima run_client.sh"
  exit 1
fi

source "$VENV_DIR/bin/activate"

echo "[INFO] Genero requirements.txt aggiornato..."
pip freeze > requirements.txt
echo "[INFO] Fatto. requirements.txt aggiornato."

