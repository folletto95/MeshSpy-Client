# backend/main.py
from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, WebSocket, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

from backend.services.mqtt import mqtt_service, get_mqtt_service
from backend.services.db import get_display_name, load_nodes_as_dict
from backend.routes import ws_logs
from backend.metrics import nodes_total, nodes_with_gps

api_router = APIRouter()

# ────────────────────────────────────────────────────────────────────────────
# .env & logging
# ────────────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("meshspy.main")

# ────────────────────────────────────────────────────────────────────────────
# FastAPI app with lifespan
# ────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.services.db import load_nodes_as_dict
    AppState().nodes.update(load_nodes_as_dict())  # Restore nodi da DB
    asyncio.create_task(mqtt_service.start())
    logger.info("MQTT listener avviato in background")
    yield
    await mqtt_service.stop()
    logger.info("MQTT listener fermato")
await mqtt_service.stop()
    logger.info("MQTT listener fermato")

app = FastAPI(title="MeshSpy API", version="0.0.1", lifespan=lifespan)

app.include_router(ws_logs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────────────────
# Prometheus metrics
# ────────────────────────────────────────────────────────────────────────────
@app.get("/metrics", include_in_schema=False)
async def metrics() -> PlainTextResponse:
    nodes = load_nodes_as_dict()
    nodes_total.set(len(nodes))
    gps_nodes = sum(1 for node in nodes.values() if node.data.get("latitude") and node.data.get("longitude"))
    nodes_with_gps.set(gps_nodes)
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ────────────────────────────────────────────────────────────────────────────
# Static GUI root
# ────────────────────────────────────────────────────────────────────────────
@app.get("/")
async def root() -> FileResponse:
    index = ROOT_DIR / "static" / "index.html"
    return FileResponse(index) if index.exists() else PlainTextResponse("MeshSpy API")

# ────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ────────────────────────────────────────────────────────────────────────────
class WiFiConfig(BaseModel):
    ssid: str
    password: str
    broker_host: str | None = None
    broker_port: int | None = None

class RequestLocation(BaseModel):
    node_id: str

# ────────────────────────────────────────────────────────────────────────────
# Health check
# ────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

# ────────────────────────────────────────────────────────────────────────────
# List nodes (REST)
# ────────────────────────────────────────────────────────────────────────────
@app.get("/nodes")
def list_nodes(svc=Depends(get_mqtt_service)) -> dict[str, dict]:
    return {
        str(node_id): {
            "name": get_display_name(node_id),
            "data": payload.data,
        }
        for node_id, payload in svc.nodes.items()
    }
# ────────────────────────────────────────────────────────────────────────────
# WebSocket streaming
# ────────────────────────────────────────────────────────────────────────────
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

# ────────────────────────────────────────────────────────────────────────────
# Request location (POST)
# ────────────────────────────────────────────────────────────────────────────
@app.post("/request-location")
async def request_location(data: RequestLocation, svc=Depends(get_mqtt_service)):
    topic = f"mesh/request/{data.node_id}/location"
    payload = json.dumps({"cmd": "request_position"})
    if svc.client:
        await svc.client.publish(topic, payload.encode())
        logger.info("Comando 'request_position' inviato a %s su topic %s", data.node_id, topic)
    else:
        logger.error("MQTT client non inizializzato, impossibile inviare comando.")
    return {"status": "ok", "requested": data.node_id}
