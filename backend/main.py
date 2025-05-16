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
from backend.services.db import get_display_name
from backend.routes import ws_logs

# ────────────────────────────────────────────────────────────────────────────
# .env & logging
# ────────────────────────────────────────────────────────────────────────────
# .env si trova due livelli sopra (project root)
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("meshspy.main")

# ────────────────────────────────────────────────────────────────────────────
# FastAPI app con lifespan
# ────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Avvia in background il listener MQTT
    asyncio.create_task(mqtt_service.start())
    logger.info("MQTT listener avviato in background")
    yield
    await mqtt_service.stop()
    logger.info("MQTT listener fermato")

app = FastAPI(title="MeshSpy API", version="0.0.1", lifespan=lifespan)

# Include il router per lo streaming dei log
app.include_router(ws_logs.router)

# CORS (sviluppo); restringere in produzione!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────────────────
# Endpoint Prometheus
# ────────────────────────────────────────────────────────────────────────────
@app.get("/metrics", include_in_schema=False)
async def metrics() -> PlainTextResponse:
    data = generate_latest()
    return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)

# ────────────────────────────────────────────────────────────────────────────
# Static GUI root
# ────────────────────────────────────────────────────────────────────────────
@app.get("/")
async def root() -> FileResponse | PlainTextResponse:
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
async def list_nodes(svc=Depends(get_mqtt_service)) -> dict[str, dict]:
    return {
        str(node_id): {
            "name": get_display_name(node_id),
            "data": payload,
        }
        for node_id, payload in svc.nodes.items()
    }

# ────────────────────────────────────────────────────────────────────────────
# WiFi config generator
# ────────────────────────────────────────────────────────────────────────────
@app.post("/wifi-config")
async def wifi_config(cfg: WiFiConfig) -> dict[str, str]:
    cfg_dict = {
        "wifi": {"ssid": cfg.ssid, "password": cfg.password},
        "mqtt": {
            "host": cfg.broker_host or mqtt_service.client._hostname,  # type: ignore
            "port": cfg.broker_port or mqtt_service.client._port,      # type: ignore
        },
    }
    import base64, yaml

    yaml_bytes = yaml.safe_dump(cfg_dict).encode()
    b64 = base64.b64encode(yaml_bytes).decode()
    return {"b64": b64}

# ────────────────────────────────────────────────────────────────────────────
# WebSocket streaming nodi
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
                    "data": data.get(),
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
