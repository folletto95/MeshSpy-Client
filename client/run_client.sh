### run_client.sh

```bash
#!/usr/bin/env bash

set -euo pipefail

# Directory del virtual environment
VENV_DIR=".venv"

# Creazione del virtual environment se non esiste
if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] Creo il virtual environment in $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
fi

# Attivazione del virtual environment
echo "[INFO] Attivo il virtual environment..."
source "$VENV_DIR/bin/activate"

# Installazione delle dipendenze
echo "[INFO] Aggiorno pip e installo dipendenze..."
python -m pip install --upgrade pip
pip install meshtastic pypubsub requests

# Avvio dello script client.py con eventuali argomenti
echo "[INFO] Avvio client.py..."
python3 client.py "$@"
```