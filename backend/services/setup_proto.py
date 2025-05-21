import os
import sys
import importlib.util
from google.protobuf.message import DecodeError
from pathlib import Path

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

# 📦 Percorso locale dove devono trovarsi già i file compilati
PROTO_DIR = os.path.join(os.path.dirname(__file__), "../meshtastic_protos")
PROTO_COMPILED_DIR = os.path.join(PROTO_DIR, "meshtastic")

def load_modules(proto_dir):
    """Carica i moduli Python generati da protoc."""
    modules = {}
    for py_file in Path(proto_dir).glob("*_pb2.py"):
        name = py_file.stem
        spec = importlib.util.spec_from_file_location(name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modules[name] = mod
    return modules

proto_modules = load_modules(PROTO_COMPILED_DIR)

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
