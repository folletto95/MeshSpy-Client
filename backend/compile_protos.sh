#!/bin/bash

# === CONFIG ===
PROTO_REPO="https://raw.githubusercontent.com/meshtastic/protobufs/refs/heads/master"
NANOPB_PROTO="https://raw.githubusercontent.com/nanopb/nanopb/refs/heads/master/generator/proto/nanopb.proto"
OUT_DIR="backend/meshtastic_protos"
PROTO_DIR="protos"
NANOPB_DIR="$PROTO_DIR/nanopb"

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

# === SETUP ===
echo "📁 Creo directory..."
mkdir -p "$PROTO_DIR" "$NANOPB_DIR" "$OUT_DIR"

echo "🧹 Pulizia vecchi file .proto..."
rm -f "$PROTO_DIR"/*.proto
rm -f "$NANOPB_DIR"/*.proto
rm -f "$OUT_DIR"/*.py

# === DOWNLOAD ===
echo "📥 Scarico i .proto..."
for file in "${PROTO_FILES[@]}"; do
  echo "➡️   $file"
  curl -sSfL "$PROTO_REPO/$file" -o "$PROTO_DIR/$file" || {
    echo "❌ Errore scaricando $file"
    exit 1
  }
done

# === NANOPB ===
echo "➡️   nanopb.proto"
curl -sSfL "$NANOPB_PROTO" -o "$NANOPB_DIR/nanopb.proto" || {
  echo "❌ Errore scaricando nanopb.proto"
  exit 1
}

# === COMPILE ===
echo "🛠️   Compilo i .proto in $OUT_DIR..."
python3 -m grpc_tools.protoc \
  --proto_path="$PROTO_DIR" \
  --proto_path="$NANOPB_DIR" \
  --python_out="$OUT_DIR" \
  "${PROTO_FILES[@]/#/$PROTO_DIR/}" "$NANOPB_DIR/nanopb.proto" || {
    echo "❌  Errore compilando i .proto"
    exit 1
}

echo "✅  Protobuf compilati con successo!"