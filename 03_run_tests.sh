#!/usr/bin/env bash
set -euo pipefail

source backend/.venv/bin/activate

echo "▶️   Lancio pytest…"

# Imposta il path per trovare correttamente 'backend'
PYTHONPATH=. poetry run pytest
pytest -q

echo "✅  Tutti i test sono passati."
