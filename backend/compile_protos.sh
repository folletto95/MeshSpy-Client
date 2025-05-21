#!/bin/bash

set -e  # Stoppa lo script se c'è un errore

PROTO_DIR="backend/protos/meshtastic"
OUT_DIR="backend/meshtastic_protos/meshtastic"
REPO_BASE="https://raw.githubusercontent.com/meshtastic/protobufs/master/meshtastic"
NANOPB_URL="https://raw.githubusercontent.com/nanopb/nanopb/refs/heads/master/generator/proto/nanopb.proto"

# Lista ufficiale (NON TOCCARE)
PROTO_FILES=(
    "admin.proto" "apponly.proto" "atak.proto" "cannedmessages.proto"
    "channel.proto" "clientonly.proto" "config.proto" "connection_status.proto"
    "device_ui.proto" "deviceonly.proto" "interdevice.proto" "localonly.proto"
    "mesh.proto" "module_config.proto" "mqtt.proto" "paxcount.proto"
    "portnums.proto" "powermon.proto" "remote_hardware.proto" "rtttl.proto"
    "storeforward.proto" "telemetry.proto" "xmodem.proto"
)

# Attiva il venv - cambia path se serve
source ../backend/.venv/bin/activate

echo "📁 Creo directory..."
mkdir -p "$PROTO_DIR"
mkdir -p "$OUT_DIR"

echo "📥 Scarico i .proto..."
# Scarica i file Meshtastic
for file in "${PROTO_FILES[@]}"; do
    url="${REPO_BASE}/${file}"
    echo "➡️  $file"
    curl -sfL "$url" -o "${PROTO_DIR}/${file}" || {
        echo "❌ Errore scaricando $file"
        exit 1
    }
done

# Scarica nanopb.proto se non esiste già
if [ ! -f "${PROTO_DIR}/nanopb.proto" ]; then
    echo "➡️  nanopb.proto"
    curl -sfL "$NANOPB_URL" -o "${PROTO_DIR}/nanopb.proto" || {
        echo "❌ Errore scaricando nanopb.proto"
        exit 1
    }
else
    echo "✅ nanopb.proto già presente, salto download."
fi

echo "🛠️  Compilo i .proto in $OUT_DIR..."
python -m grpc_tools.protoc \
  -Ibackend/protos \
  -Ibackend/protos/meshtastic \
  --python_out=backend/meshtastic_protos \
  backend/protos/meshtastic/*.proto || {
    echo "❌ Errore compilando i .proto"
    exit 1
}

echo "📦 Aggiungo __init__.py..."
touch backend/meshtastic_protos/__init__.py
touch backend/meshtastic_protos/meshtastic/__init__.py

echo "✅ Tutto fatto!"
