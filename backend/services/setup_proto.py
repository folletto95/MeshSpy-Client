import os
import subprocess
import requests
from pathlib import Path

PROTO_DIR = Path(__file__).resolve().parent.parent / "meshtastic_protos"
BASE_URL = "https://raw.githubusercontent.com/meshtastic/protobufs/master/meshtastic"

PROTO_FILES = [
    "admin.proto", "apponly.proto", "atak.proto", "cannedmessages.proto",
    "channel.proto", "clientonly.proto", "config.proto", "connection_status.proto",
    "device_ui.proto", "deviceonly.proto",
    "interdevice.proto", "localonly.proto", "mesh.proto", "module_config.proto",
    "mqtt.proto", "paxcount.proto", "portnums.proto", "powermon.proto",
    "remote_hardware.proto", "routing.proto", "rtttl.proto", "storeforward.proto",
    "telemetry.proto", "util.proto", "xmodem.proto"
]

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        open(init_file, "w").close()

def download_protos(dest_dir):
    for proto in PROTO_FILES:
        url = f"{BASE_URL}/{proto}"
        print(f"Scarico {proto}...")
        r = requests.get(url)
        r.raise_for_status()
        with open(os.path.join(dest_dir, proto), "wb") as f:
            f.write(r.content)

def compile_protos(proto_dir):
    print("Compilo i file .proto...")
    result = subprocess.run([
        "protoc",
        f"--proto_path={proto_dir}",
        f"--python_out={proto_dir}",
        *[proto for proto in os.listdir(proto_dir) if proto.endswith(".proto")]
    ], cwd=proto_dir, capture_output=True)
    if result.returncode != 0:
        print("Errore durante la compilazione:")
        print(result.stderr.decode())
        exit(1)

def main():
    ensure_directory(PROTO_DIR)
    download_protos(PROTO_DIR)
    compile_protos(PROTO_DIR)
    print("✅ Moduli protobuf pronti.")
