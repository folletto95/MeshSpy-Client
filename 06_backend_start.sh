#!/usr/bin/env bash
set -euo pipefail
ROOT="$(dirname "$(realpath "$0")")"

# attiva la venv
source "$ROOT/backend/.venv/bin/activate"

# chiude eventuali processi uvicorn già attivi
if pgrep -f "uvicorn backend.main:app" > /dev/null; then
  echo "⚠️  Uvicorn già in esecuzione. Termino il processo..."
  pkill -f "uvicorn backend.main:app"
  sleep 1
fi

echo "▶️  Avvio backend FastAPI su http://localhost:8000 ..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
echo "ℹ️  Backend PID: $!"
