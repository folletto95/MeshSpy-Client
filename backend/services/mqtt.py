import asyncio
import json
import logging
import os
from contextlib import AsyncExitStack
from typing import Optional, Dict

from aiomqtt import Client, MqttError
from dotenv import load_dotenv

from backend.services.db import (
    init_db,
    load_nodes_from_db,
    update_position,
    update_nodeinfo,
    get_db_path,
)

# ────────────────────────────────────────────────────────────────────────────
# Carica .env dal progetto
# ────────────────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

logger = logging.getLogger("meshspy.mqtt")

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "meshspy/nodes/#")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# ────────────────────────────────────────────────────────────────────────────
# Data holder
# ────────────────────────────────────────────────────────────────────────────
class NodeData:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

# ────────────────────────────────────────────────────────────────────────────
# Il nostro singleton MQTTService
# ────────────────────────────────────────────────────────────────────────────
class MQTTService:
    def __init__(self) -> None:
        self.client: Optional[Client] = None
        self._stack: Optional[AsyncExitStack] = None
        # carica dallo storico DB all’avvio
        raw = load_nodes_from_db()
        self.nodes: Dict[str, NodeData] = {
            str(r["node_id"]): NodeData(name=r.get("name", ""), data={})
            for r in raw
        }
        self.db_path = get_db_path()
        self.my_node_id = "Server-MeshSpy"

    async def start(self) -> None:
        logger.info("🗄️  DB path MQTT: %s", self.db_path)
        init_db()

        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        # connessione
        self.client = await self._stack.enter_async_context(
            Client(
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                username=MQTT_USERNAME or None,
                password=MQTT_PASSWORD or None,
                keepalive=60,
            )
        )

        await self.client.subscribe(MQTT_TOPIC)
        logger.info("✅ MQTT connesso a %s:%s, topic %r", MQTT_HOST, MQTT_PORT, MQTT_TOPIC)

        # avvia listener
        asyncio.create_task(self._listener(), name="mqtt-listener")

    async def stop(self) -> None:
        if self._stack:
            await self._stack.aclose()
        logger.info("MQTT listener fermato")

    async def _listener(self) -> None:
        assert self.client is not None
        try:
            async for msg in self.client.messages:
                await self._handle_message(msg.topic, msg.payload)
        except MqttError as e:
            logger.error("Errore MQTT listener: %s", e)

    async def _handle_message(self, topic: str, payload: bytes) -> None:
        # parsing JSON
        try:
            msg = json.loads(payload.decode())
        except Exception as e:
            logger.warning("Payload non JSON su %s: %s", topic, e)
            return

        node_id = str(msg.get("from") or msg.get("node_id"))
        if not node_id or node_id == self.my_node_id:
            return

        cmd = msg.get("cmd")
        if cmd == "position":
            lat, lon = msg.get("lat"), msg.get("lon")
            if lat is not None and lon is not None:
                logger.info("📍 Posizione %s → (%s, %s)", node_id, lat, lon)
                update_position(node_id, lat, lon)
                self.nodes[node_id] = NodeData(name=node_id, data=msg)
        elif cmd == "nodeinfo":
            name = msg.get("name")
            if name:
                logger.info("ℹ️  Nodeinfo %s → %s", node_id, name)
                update_nodeinfo(node_id, name)
                self.nodes[node_id] = NodeData(name=name, data=msg)
        else:
            logger.debug("MQTT msg sconosciuto %r da %s", cmd, node_id)

# singleton e dependency
mqtt_service = MQTTService()

def get_mqtt_service() -> MQTTService:
    return mqtt_service
