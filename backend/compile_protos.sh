#!/bin/bash
set -e

# === CONFIG ===
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROTO_PARENT_DIR="$SCRIPT_DIR/protos"
MESHTASTIC_DIR="$PROTO_PARENT_DIR/meshtastic"
NANOPB_DIR="$PROTO_PARENT_DIR/nanopb"
OUT_DIR="$SCRIPT_DIR/meshtastic_protos"
MESHTASTIC_REPO="https://raw.githubusercontent.com/meshtastic/protobufs/v2.6.8/meshtastic"
NANOPB_URL="https://raw.githubusercontent.com/nanopb/nanopb/refs/heads/master/generator/proto/nanopb.proto"

# === LISTA PROTO UFFICIALE - NON TOCCARE   ===
PROTO_FILES=(
  "admin.proto" "apponly.proto" "atak.proto" "cannedmessages.proto"
  "channel.proto" "clientonly.proto" "config.proto"
  "connection_status.proto" "device_ui.proto" "deviceonly.proto"
  "interdevice.proto" "localonly.proto" "mesh.proto"
  "module_config.proto" "mqtt.proto" "paxcount.proto"
  "portnums.proto" "powermon.proto" "remote_hardware.proto"
  "rtttl.proto" "storeforward.proto" "telemetry.proto" "xmodem.proto"
)


PYTHON_BIN="${VENV_PYTHON:-$(which python3)}"
command -v "$PYTHON_BIN" >/dev/null || { echo "❌ Python non trovato."; exit 1; }

echo "📦 Installo dipendenze..."
"$PYTHON_BIN" -m pip install -r requirements.txt

echo "🧹 Pulizia..."
rm -rf "$MESHTASTIC_DIR" "$NANOPB_DIR"
mkdir -p "$MESHTASTIC_DIR" "$NANOPB_DIR" "$OUT_DIR"

echo "📥 Scarico i .proto Meshtastic..."
for proto in "${PROTO_FILES[@]}"; do
  echo "➡️  $proto"
  curl -sfL "$MESHTASTIC_REPO/$proto" -o "$MESHTASTIC_DIR/$proto"
done

echo "📥 Scarico nanopb.proto..."
curl -sfL "$NANOPB_URL" -o "$NANOPB_DIR/nanopb.proto"

echo "🛠️  Compilo i .proto in $OUT_DIR..."
"$PYTHON_BIN" -m grpc_tools.protoc \
  -I "$PROTO_PARENT_DIR" \
  -I "$NANOPB_DIR" \
  --python_out="$OUT_DIR" \
  $(find "$MESHTASTIC_DIR" -name "*.proto")

echo "✅ Compilazione completata!"