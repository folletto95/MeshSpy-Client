import os
import subprocess
import requests
import time
from pathlib import Path

# Base path settings
BASE_DIR = Path(__file__).resolve().parent.parent
PROTO_ROOT = BASE_DIR / "meshtastic_protos"
PROTO_DIR = PROTO_ROOT / "meshtastic"
NANOPB_DIR = PROTO_ROOT / "nanopb"
BASE_URL = "https://raw.githubusercontent.com/meshtastic/protobufs/master/meshtastic"
NANOPB_URL = "https://raw.githubusercontent.com/nanopb/nanopb/master/generator/proto/nanopb.proto"

# Full .proto file list from repo
PROTO_FILES = [
    "admin.proto", "apponly.proto", "atak.proto", "cannedmessages.proto",
    "channel.proto", "clientonly.proto", "config.proto", "connection_status.proto",
    "device_ui.proto", "deviceonly.proto", "interdevice.proto", "localonly.proto",
    "mesh.proto", "module_config.proto", "mqtt.proto", "paxcount.proto",
    "portnums.proto", "powermon.proto", "remote_hardware.proto", "rtttl.proto",
    "storeforward.proto", "telemetry.proto", "xmodem.proto"
]

def ensure_directory(path):
    os.makedirs(path, exist_ok=True)
    init_file = path / "__init__.py"
    if not init_file.exists():
        init_file.touch()

def download_with_retry(url, dest_path, max_retries=3, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(dest_path, "wb") as f:
                f.write(r.content)
            return
        except Exception as e:
            print(f"[Tentativo {attempt}] Errore durante il download da {url}: {e}")
            if attempt < max_retries:
                print(f"Aspetto {delay} secondi e ritento...")
                time.sleep(delay)
            else:
                print(f"❌ Impossibile scaricare {url} dopo {max_retries} tentativi.")
                raise

def download_protos(dest_dir):
    for proto in PROTO_FILES:
        url = f"{BASE_URL}/{proto}"
        print(f"📥 Scarico {proto}...")
        download_with_retry(url, dest_dir / proto)

def download_nanopb(dest_dir):
    print("📥 Scarico nanopb.proto...")
    dest_path = dest_dir / "nanopb.proto"
    download_with_retry(NANOPB_URL, dest_path)

def compile_protos(proto_root):
    print("🛠️  Compilo i file .proto...")
    result = subprocess.run([
        "protoc",
        f"--proto_path={proto_root}",
        f"--proto_path={proto_root / 'nanopb'}",
        f"--python_out={proto_root}",
        *[str(Path("meshtastic") / proto) for proto in PROTO_FILES]
    ], cwd=proto_root, capture_output=True)
    if result.returncode != 0:
        print("❌ Errore durante la compilazione:")
        print(result.stderr.decode())
        exit(1)

def main():
    ensure_directory(PROTO_DIR)
    ensure_directory(NANOPB_DIR)
    download_protos(PROTO_DIR)
    download_nanopb(NANOPB_DIR)
    compile_protos(PROTO_ROOT)
    print("✅ Moduli protobuf pronti.")

# Questo controllo permette anche l'import di main() da altri file (come in mqtt.py)
if __name__ == "__main__":
    main()
