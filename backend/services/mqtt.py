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
# Caricamento .env (project root, due livelli sopra questo file)
# ────────────────────────────────────────────────────────────────────────────
ENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env")
)
load_dotenv(ENV_PATH)

logger = logging.getLogger("meshspy.mqtt")

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "meshspy/nodes/#")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")


class NodeData:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data


class MQTTService:
    def __init__(self) -> None:
        # Inizializza il DB e carica lo storico dei nodi
        init_db()
        raw = load_nodes_from_db()
        self.nodes: Dict[str, NodeData] = {}
        for r in raw:
            key = r.get("node_id") or r.get("id")
            if not key:
                continue
            self.nodes[str(key)] = NodeData(name=r.get("name", ""), data={})

        self.client: Optional[Client] = None
        self._stack: Optional[AsyncExitStack] = None
        self.db_path = get_db_path()
        self.my_node_id = "Server-MeshSpy"

    async def start(self) -> None:
        logger.info("🗄️  DB path MQTT: %s", self.db_path)
        attempts = 0

        # Retry esponenziale finché il broker non risponde
        while True:
            try:
                self._stack = AsyncExitStack()
                await self._stack.__aenter__()

                logger.info(
                    "🔌 Tentativo connessione MQTT a %s:%s (topic %r)",
                    MQTT_HOST, MQTT_PORT, MQTT_TOPIC,
                )
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
                logger.info(
                    "✅ Connesso al broker %s:%s, sottoscritto a %r",
                    MQTT_HOST, MQTT_PORT, MQTT_TOPIC,
                )

                # Avvia il listener in background
                asyncio.create_task(self._listener(), name="mqtt-listener")
                return

            except MqttError as exc:
                attempts += 1
                delay = min(60, 2 ** attempts)
                logger.error(
                    "❌ Connessione MQTT fallita (tentativo #%d): %s; riprovo tra %ds",
                    attempts, exc, delay,
                )
                if self._stack:
                    await self._stack.aclose()
                await asyncio.sleep(delay)

    async def stop(self) -> None:
        if self._stack:
            await self._stack.aclose()
        logger.info("🛑 MQTT listener fermato")

    async def _listener(self) -> None:
        assert self.client is not None
        try:
            async for msg in self.client.messages:
                await self._handle_message(msg.topic, msg.payload)
        except MqttError as e:
            logger.error("Errore MQTT listener: %s", e)

    async def _handle_message(self, topic: str, payload: bytes) -> None:
        try:
            message = json.loads(payload.decode("utf-8"))
        except Exception as e:
            logger.warning("❓ Payload non JSON su %s: %s", topic, e)
            return

        node_id = message.get("from")
        if not node_id or node_id == self.my_node_id:
            return

        cmd = message.get("cmd")
        if cmd == "position":
            lat, lon = message.get("lat"), message.get("lon")
            if lat is not None and lon is not None:
                logger.info("📍 Posizione %s → (%s, %s)", node_id, lat, lon)
                update_position(node_id, lat, lon)
                self.nodes[node_id] = NodeData(name=node_id, data=message)
        elif cmd == "nodeinfo":
            name = message.get("name")
            if name:
                logger.info("ℹ️  Nodeinfo %s → %s", node_id, name)
                update_nodeinfo(node_id, name)
                self.nodes[node_id] = NodeData(name=name, data=message)
        else:
            logger.debug("🔄 Msg sconosciuto (%s) da %s", cmd or "", node_id)


# Singleton e dependency
mqtt_service = MQTTService()

def get_mqtt_service() -> MQTTService:
    return mqtt_service
