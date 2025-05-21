#!/bin/bash

set -e

# === CONFIG ===
PROTO_DIR="backend/protos/meshtastic"
OUT_DIR="backend/meshtastic_protos"
MESHTASTIC_VERSION="v2.1.11"  # ✅ Usa una versione stabile
MESHTASTIC_REPO="https://raw.githubusercontent.com/meshtastic/protobufs/${MESHTASTIC_VERSION}/meshtastic"
NANOPB_URL="https://raw.githubusercontent.com/nanopb/nanopb/refs/heads/master/generator/proto/nanopb.proto"

# === LISTA PROTO UFFICIALE - NON TOCCARE ===
PROTO_FILES=(
  "admin.proto" "apponly.proto" "atak.proto" "cannedmessages.proto"
  "channel.proto" "clientonly.proto" "config.proto"
  "connection_status.proto" "device_ui.proto" "deviceonly.proto"
  "interdevice.proto" "localonly.proto" "mesh.proto"
  "module_config.proto" "mqtt.proto" "paxcount.proto"
  "portnums.proto" "powermon.proto" "remote_hardware.proto"
  "rtttl.proto" "storeforward.proto" "telemetry.proto" "xmodem.proto"
)

# === VERIFICHE AMBIENTE ===
command -v protoc >/dev/null 2>&1 || { echo "❌ 'protoc' non trovato. Installalo prima di procedere."; exit 1; }
PYTHON_BIN="${VENV_PYTHON:-$(which python3)}"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "❌ Python non trovato."; exit 1; }

# === PREPARAZIONE ===
echo "🧹 Pulizia vecchi file .proto..."
rm -rf "$PROTO_DIR"
mkdir -p "$PROTO_DIR"
mkdir -p "$OUT_DIR"

echo "📥 Scarico i .proto..."

# Scarica i file .proto principali
for proto in "${PROTO_FILES[@]}"; do
  echo "➡️  $proto"
  curl -sfL "$MESHTASTIC_REPO/$proto" -o "$PROTO_DIR/$proto" || {
    echo "❌ Errore scaricando $proto"
    exit 1
  }
done

# Scarica nanopb.proto se non esiste
if [ ! -f "${PROTO_DIR}/nanopb.proto" ]; then
  echo "➡️  nanopb.proto"
  curl -sfL "$NANOPB_URL" -o "${PROTO_DIR}/nanopb.proto" || {
    echo "❌ Errore scaricando nanopb.proto"
    exit 1
  }
else
  echo "✅ nanopb.proto già presente, salto download."
fi

# === COMPILAZIONE ===
echo "🛠️  Compilo i .proto in $OUT_DIR..."

for file in "${PROTO_FILES[@]}"; do
  "$PYTHON_BIN" -m grpc_tools.protoc \
    -Ibackend/protos \
    -Ibackend/protos/meshtastic \
    --python_out="$OUT_DIR" \
    "$PROTO_DIR/$file" || {
      echo "❌ Errore compilando $file"
      exit 1
  }
done

echo "✅ Compilazione completata!"
