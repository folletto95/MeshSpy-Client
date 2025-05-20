#!/usr/bin/env bash

set -euo pipefail

echo "[UPDATE] Aggiornamento in corso..."

# Vai nella directory del progetto (modifica se necessario)
cd "$(dirname "$0")"

# Aggiorna dal repository git
echo "[UPDATE] Eseguo git pull..."
git pull || echo "[WARNING] git pull fallito"

# Aggiorna il virtualenv e le dipendenze
echo "[UPDATE] Aggiorno le dipendenze Python..."
source .venv/bin/activate
pip install -r requirements.txt

# Riavvia il processo se gestito da systemd (opzionale)
if systemctl is-active --quiet meshspy-client.service; then
  echo "[UPDATE] Riavvio servizio systemd..."
  sudo systemctl restart meshspy-client.service
fi

echo "[UPDATE] Completato con successo."
