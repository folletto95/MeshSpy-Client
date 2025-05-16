#!/usr/bin/env bash
set -euo pipefail
ROOT="$(dirname "$(realpath "$0")")"

# attiva la venv
source "$ROOT/backend/.venv/bin/activate"

# chiude il processo che occupa la porta 8000 se esiste
if lsof -i:8000 &> /dev/null; then
  echo "⚠️  Porta 8000 occupata. Uccido il processo che la sta usando..."
  PID=$(lsof -ti:8000)
  kill -9 $PID
  sleep 1
fi

echo "▶️  Avvio backend FastAPI su http://localhost:8000 ..."
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
echo "ℹ️  Backend PID: $!"
