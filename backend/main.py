from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, WebSocket, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

from backend.services.mqtt import mqtt_service, get_mqtt_service
from backend.services.db import get_display_name, load_nodes_as_dict
from backend.routes import ws_logs
from backend.metrics import nodes_total, nodes_with_gps
from backend.state import AppState

api_router = APIRouter()

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "meshtastic_protos"))

# .env & logging
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("meshspy.main")

PROTO_REPO = "https://github.com/meshtastic/protobufs"
PROTO_DIR = ROOT_DIR / "meshtastic_protos"
COMPILED_DIR = ROOT_DIR / "meshtastic_protos" / "meshtastic"

def ensure_protobufs_compiled():
    if not COMPILED_DIR.exists() or not any(COMPILED_DIR.glob("*_pb2.py")):
        logger.info("📥 Scarico e compilo i file protobuf di Meshtastic...")
        if PROTO_DIR.exists():
            shutil.rmtree(PROTO_DIR)
        subprocess.run(["git", "clone", PROTO_REPO, str(PROTO_DIR)], check=True)
        subprocess.run([
            "python", "-m", "grpc_tools.protoc",
            "-I", str(PROTO_DIR),
            "--python_out", str(PROTO_DIR),
            *(str(p) for p in Path(PROTO_DIR).glob("*.proto"))
        ], check=True)
        (PROTO_DIR / "__init__.py").touch()
        (COMPILED_DIR / "__init__.py").touch()
        logger.info("✅ Compilazione completata.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_protobufs_compiled()
    AppState().nodes.update(load_nodes_as_dict())
    logger.info("📦 Nodi caricati dal DB all'avvio")
    asyncio.create_task(mqtt_service.start())
    logger.info("MQTT listener avviato in background")
    yield

app = FastAPI(title="MeshSpy API", version="0.0.1", lifespan=lifespan)
app.include_router(ws_logs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics", include_in_schema=False)
async def metrics() -> PlainTextResponse:
    nodes = load_nodes_as_dict()
    nodes_total.set(len(nodes))
    gps_nodes = sum(1 for node in nodes.values() if node.data.get("latitude") and node.data.get("longitude"))
    nodes_with_gps.set(gps_nodes)
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root() -> FileResponse:
    index = ROOT_DIR / "static" / "index.html"
    return FileResponse(index) if index.exists() else PlainTextResponse("MeshSpy API")

class WiFiConfig(BaseModel):
    ssid: str
    password: str
    broker_host: str | None = None
    broker_port: int | None = None

class RequestLocation(BaseModel):
    node_id: str

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/nodes")
def list_nodes(svc=Depends(get_mqtt_service)) -> dict[str, dict]:
    return {
        str(node_id): {
            "name": get_display_name(node_id),
            "data": payload.data,
        }
        for node_id, payload in svc.nodes.items()
    }

@app.websocket("/ws/nodes")
async def ws_nodes(ws: WebSocket, svc=Depends(get_mqtt_service)) -> None:
    await ws.accept()
    last: dict[str, Any] | None = None
    try:
        while True:
            await asyncio.sleep(0.5)
            current = {
                nid: {
                    "name": get_display_name(nid),
                    "data": data.data,
                }
                for nid, data in svc.nodes.items()
            }
            if current != last:
                await ws.send_json(current)
                last = current
    except Exception as exc:
        logger.warning("WebSocket chiuso: %s", exc)
    finally:
        await ws.close()

@app.post("/request-position")
async def request_position(data: RequestLocation, svc=Depends(get_mqtt_service)):
    topic = f"mesh/request/{data.node_id}/location"
    payload = json.dumps({"cmd": "request_position", "from": "Server-MeshSpy"})

    if not svc.connected or svc.client is None:
        logger.warning("⛔ MQTT non pronto: client mancante o disconnesso.")
        raise HTTPException(status_code=503, detail="MQTT client not ready")

    try:
        await svc.client.publish(topic, payload.encode())
    except Exception as e:
        logger.error("❌ Errore pubblicando su MQTT: %s", e)
        raise HTTPException(status_code=500, detail="Errore pubblicando su MQTT")

    logger.info("📡 Richiesta posizione inviata a %s su topic %s", data.node_id, topic)
    return {"status": "ok", "requested": data.node_id}
