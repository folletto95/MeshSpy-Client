#!/usr/bin/env bash
set -euo pipefail

ROOT="$(dirname "$(realpath "$0")")"

echo "▶️  Avvio backend ..."
bash "$ROOT/06_backend_start.sh"

echo "▶️  Avvio frontend con proxy /api → localhost:8000 ..."
# Vai nella dir del frontend
cd "$ROOT/meshspy-ui"

# Lancia Vite (usa il vite.config.js con proxy)
npm run dev -- --host 0.0.0.0 --port 5173
