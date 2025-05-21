import os
import sys
import tempfile
import subprocess
import importlib.util
from google.protobuf.message import DecodeError
import requests
from pathlib import Path

# Percorso base ufficiale dei file .proto
MESHTASTIC_PROTO_BASE = "https://raw.githubusercontent.com/meshtastic/protobufs/refs/heads/master/meshtastic/"

MESHTASTIC_PROTO_FILES = [
    "admin.proto", "apponly.proto", "atak.proto", "cannedmessages.proto", 
    "channel.proto", "clientonly.proto", "config.proto",
    "connection_status.proto", "device_ui.proto", "deviceonly.proto",
    "interdevice.proto", "localonly.proto", "mesh.proto", 
    "module_config.proto", "mqtt.proto", "paxcount.proto", 
    "portnums.proto", "powermon.proto", "remote_hardware.proto", 
    "rtttl.proto", "storeforward.proto", "telemetry.proto", "xmodem.proto"
]

def download_all_protos(proto_dir):
    """Scarica tutti i file .proto dal repository Meshtastic se non esistono."""
    for proto in MESHTASTIC_PROTO_FILES:
        proto_path = os.path.join(proto_dir, proto)
        if not os.path.exists(proto_path):
            print(f"📥 Scarico {proto}...")
            url = f"{MESHTASTIC_PROTO_BASE}/{proto}"
            response = requests.get(url)
            response.raise_for_status()
            with open(proto_path, "wb") as f:
                f.write(response.content)
        else:
            print(f"✅ {proto} già presente, skip.")

def compile_protos(proto_dir):
    """Compila i .proto in moduli Python usando protoc."""
    proto_files = [str(f) for f in Path(proto_dir).glob("*.proto")]
    result = subprocess.run(
        ["protoc", "--proto_path", proto_dir, "--python_out", proto_dir] + proto_files,
        cwd=proto_dir,
        capture_output=True,
    )
    if result.returncode != 0:
        print("Errore compilando i .proto:", result.stderr.decode())
        sys.exit(1)

def load_modules(proto_dir):
    """Carica dinamicamente i moduli Python generati da protoc."""
    modules = {}
    for py_file in Path(proto_dir).glob("*_pb2.py"):
        name = py_file.stem
        spec = importlib.util.spec_from_file_location(name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modules[name] = mod
    return modules

# Preparazione moduli protobuf al volo
PROTO_DIR = tempfile.mkdtemp()
download_all_protos(PROTO_DIR)
compile_protos(PROTO_DIR)
proto_modules = load_modules(PROTO_DIR)

mqtt_pb2 = proto_modules["mqtt_pb2"]
mesh_pb2 = proto_modules["mesh_pb2"]

def decode_meshtastic_message(payload_bytes):
    """Decodifica un payload MQTT Meshtastic in formato Protobuf."""
    try:
        envelope = mqtt_pb2.ServiceEnvelope()
        envelope.ParseFromString(payload_bytes)

        decoded = {
            "channel_id": envelope.channel_id,
            "gateway_id": envelope.gateway_id,
        }

        if envelope.HasField("packet"):
            data_packet = mesh_pb2.Data()
            data_packet.ParseFromString(envelope.packet)
            decoded["packet"] = data_packet
        else:
            decoded["packet"] = None

        return decoded

    except DecodeError as e:
        print(f"Errore nella decodifica: {e}")
        return None
