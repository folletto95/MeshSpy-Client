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

# ⚠️ NON TOCCARE QUESTA LISTA
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
    """Scarica i file .proto nella struttura corretta solo se mancanti."""
    meshtastic_dir = os.path.join(proto_dir, "meshtastic")
    os.makedirs(meshtastic_dir, exist_ok=True)
    for proto in MESHTASTIC_PROTO_FILES:
        proto_path = os.path.join(meshtastic_dir, proto)
        if not os.path.exists(proto_path):
            print(f"📥 Scarico {proto}...")
            url = f"{MESHTASTIC_PROTO_BASE}{proto}"
            response = requests.get(url)
            if response.status_code == 404:
                print(f"❌ ERRORE 404: {url}")
                continue
            response.raise_for_status()
            with open(proto_path, "wb") as f:
                f.write(response.content)
        else:
            print(f"✅ {proto} già presente, skip.")

def compile_protos(proto_dir):
    """Compila i file .proto in Python usando protoc."""
    meshtastic_dir = os.path.join(proto_dir, "meshtastic")
    proto_files = [str(f) for f in Path(meshtastic_dir).glob("*.proto")]
    result = subprocess.run(
        ["protoc", "--proto_path=meshtastic", "--python_out=meshtastic"] + [f.name for f in Path(meshtastic_dir).glob("*.proto")],
        cwd=proto_dir,
        capture_output=True,
    )
    if result.returncode != 0:
        print("❌ Errore compilando i .proto:")
        print(result.stderr.decode())
        sys.exit(1)

def load_modules(proto_dir):
    """Carica i moduli Python generati da protoc."""
    modules = {}
    meshtastic_dir = os.path.join(proto_dir, "meshtastic")
    for py_file in Path(meshtastic_dir).glob("*_pb2.py"):
        name = py_file.stem
        spec = importlib.util.spec_from_file_location(name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modules[name] = mod
    return modules

# ▶️ Esecuzione
PROTO_DIR = tempfile.mkdtemp()
download_all_protos(PROTO_DIR)
compile_protos(PROTO_DIR)
proto_modules = load_modules(PROTO_DIR)

mqtt_pb2 = proto_modules.get("mqtt_pb2")
mesh_pb2 = proto_modules.get("mesh_pb2")

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
        print(f"❌ Errore decodifica protobuf: {e}")
        return None
