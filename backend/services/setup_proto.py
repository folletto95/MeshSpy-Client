
import os
import subprocess
import requests
from pathlib import Path

# Base path settings
BASE_DIR = Path(__file__).resolve().parent.parent
PROTO_ROOT = BASE_DIR / "meshtastic_protos"
PROTO_DIR = PROTO_ROOT / "meshtastic"
BASE_URL = "https://raw.githubusercontent.com/meshtastic/protobufs/master/meshtastic"

# Full .proto file list from repo
PROTO_FILES = [
    "admin.proto", "apponly.proto", "atak.proto", "cannedmessages.proto",
    "channel.proto", "clientonly.proto", "config.proto", "connection_status.proto",
    "device_ui.proto", "deviceonly.proto",
    "interdevice.proto", "localonly.proto", "mesh.proto", "module_config.proto",
    "mqtt.proto", "paxcount.proto", "portnums.proto", "powermon.proto",
    "remote_hardware.proto", "rtttl.proto", "storeforward.proto",
    "telemetry.proto", "xmodem.proto"
]

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)
    init_file = path / "__init__.py"
    if not init_file.exists():
        init_file.touch()

def download_protos(dest_dir):
    for proto in PROTO_FILES:
        url = f"{BASE_URL}/{proto}"
        print(f"Scarico {proto}...")
        r = requests.get(url)
        r.raise_for_status()
        with open(dest_dir / proto, "wb") as f:
            f.write(r.content)

def compile_protos(proto_root):
    print("Compilo i file .proto...")
    result = subprocess.run([
        "protoc",
        f"--proto_path={proto_root}",
        f"--python_out={proto_root}",
        *[str(Path("meshtastic") / proto) for proto in PROTO_FILES]
    ], cwd=proto_root, capture_output=True)
    if result.returncode != 0:
        print("Errore durante la compilazione:")
        print(result.stderr.decode())
        exit(1)

def main():
    ensure_directory(PROTO_DIR)
    download_protos(PROTO_DIR)
    compile_protos(PROTO_ROOT)
    print("✅ Moduli protobuf pronti.")

if __name__ == "__main__":
    main()
