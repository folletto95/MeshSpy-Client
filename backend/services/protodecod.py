import os
import sys
import tempfile
import subprocess
import importlib.util
from google.protobuf.message import DecodeError
import requests
from pathlib import Path


def download_all_protos(proto_dir):
    """Scarica tutti i file .proto dal repository Meshtastic."""
    base_url = "https://raw.githubusercontent.com/meshtastic/protobufs/main"
    proto_files = [
        "admin.proto", "channel.proto", "config.proto", "data.proto", "device.proto",
        "environment.proto", "hardware.proto", "mesh.proto", "mqtt.proto",
        "remote_hardware.proto", "routing.proto", "store.proto", "telemetry.proto",
        "util.proto"
    ]

    for proto in proto_files:
        url = f"{base_url}/{proto}"
        response = requests.get(url)
        response.raise_for_status()
        with open(os.path.join(proto_dir, proto), "wb") as f:
            f.write(response.content)


def compile_protos(proto_dir):
    """Compila i .proto in moduli Python."""
    proto_files = list(Path(proto_dir).glob("*.proto"))
    proto_filenames = [str(p.name) for p in proto_files]
    result = subprocess.run(
        ["protoc", "--proto_path", proto_dir, "--python_out", proto_dir] + proto_filenames,
        cwd=proto_dir,
        capture_output=True,
    )
    if result.returncode != 0:
        print("Errore compilando i .proto:", result.stderr.decode())
        sys.exit(1)


def load_modules(proto_dir):
    """Carica dinamicamente tutti i moduli Python generati da protoc."""
    modules = {}
    for py_file in Path(proto_dir).glob("*_pb2.py"):
        name = py_file.stem
        spec = importlib.util.spec_from_file_location(name, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        modules[name] = mod
    return modules


# Preparazione moduli protobuf
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
            try:
                mesh_packet = mesh_pb2.MeshPacket()
                mesh_packet.ParseFromString(envelope.packet)
                decoded["packet"] = mesh_packet
            except DecodeError as dp_err:
                decoded["packet"] = f"Errore decodifica MeshPacket: {dp_err}"
        else:
            decoded["packet"] = None

        return decoded

    except DecodeError as e:
        print(f"Errore nella decodifica ServiceEnvelope: {e}")
        return None
