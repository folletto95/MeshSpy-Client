# backend/services/mqtt.py

import asyncio
import logging
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Dict
from pydantic import BaseModel
from dotenv import find_dotenv, load_dotenv
from aiomqtt import Client, MqttError

from backend.services.db import (
    register_node,
    upsert_nodeinfo,
    update_position,
    store_event,
)


class NodeData:
    def __init__(self):
        self.data: Dict[str, Any] = {}

    def update(self, new_data: Dict[str, Any]):
        for k, v in new_data.items():
            if v is not None and v != "" and self.data.get(k) != v:
                self.data[k] = v

    def get(self) -> Dict[str, Any]:
        return self.data

logger = logging.getLogger("meshspy.mqtt")

# ────────────────────────────────────────────────────────────────────────────
# Carica .env dalla radice del progetto MeshSpy
# ────────────────────────────────────────────────────────────────────────────
env_path = find_dotenv(usecwd=True)
if not env_path:
    raise RuntimeError(".env non trovato: mettilo nella radice di MeshSpy")
load_dotenv(env_path)

# ────────────────────────────────────────────────────────────────────────────
# Config MQTT
# ────────────────────────────────────────────────────────────────────────────
BROKER_HOST     = os.getenv("MQTT_HOST", "192.168.10.202")
BROKER_PORT     = int(os.getenv("MQTT_PORT", 1883))
BROKER_USERNAME = os.getenv("MQTT_USERNAME", "")
BROKER_PASSWORD = os.getenv("MQTT_PASSWORD", "")
TOPICS          = os.getenv("MQTT_TOPICS", "#").split(",")

logger.debug("Caricate da .env: HOST=%s PORT=%s USER=%r", BROKER_HOST, BROKER_PORT, BROKER_USERNAME)

class MQTTService:
    def __init__(self) -> None:
        self._stack: AsyncExitStack | None = None
        self.client: Client | None = None
        self.name_map: Dict[str, str] = {}
        self.nodes: Dict[str, NodeData] = {}
    async def start(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        self.client = Client(BROKER_HOST, BROKER_PORT, username=BROKER_USERNAME, password=BROKER_PASSWORD)
        await self._stack.enter_async_context(self.client)

        self.client.on_message = self._on_message
        for topic in TOPICS:
            await self.client.subscribe(topic)
        logger.info("Sottoscritto a %s", TOPICS)

        asyncio.create_task(self._listener())
        logger.info("In ascolto su topic MQTT")

    async def stop(self):
        if self._stack:
            await self._stack.aclose()
            logger.info("MQTT listener fermato")

    async def _listener(self):
        async with self.client.unfiltered_messages() as messages:
            async for msg in messages:
                await self._handle_message(msg.topic, msg.payload)

    async def _handle_message(self, topic: str, payload: bytes):
        try:
            decoded = payload.decode("utf-8")
            data = json.loads(decoded)
        except Exception as e:
            logger.warning("Errore nel parsing JSON del messaggio MQTT su %s: %s", topic, e)
            return

        parts = topic.split("/")
        if len(parts) < 5:
            logger.warning("Topic MQTT non riconosciuto: %s", topic)
            return

        # Estrai ID nodo (ultima parte del topic)
        node_id = parts[-1].lstrip("!")
        msg_type = data.get("type", "")

        if msg_type == "nodeinfo":
            name = data.get("longName", node_id)
            self.name_map[node_id] = name

            logger.info("Aggiornato nodeinfo per %s → %s", node_id, name)
            self.nodes.setdefault(node_id, NodeData()).update(data)

            upsert_nodeinfo(node_id, name)
            register_node(node_id)
            if "latitude" in data and "longitude" in data:
                update_position(node_id, float(data["latitude"]), float(data["longitude"]))

        elif msg_type == "traceroute":
            hops = data.get("hops", [])
            logger.info("Traceroute da %s: %s", node_id, hops)

        elif msg_type == "text":
            logger.info("Messaggio di testo da %s: %s", node_id, data.get("text", ""))

        else:
            logger.info("Tipo messaggio sconosciuto (%s) da %s", msg_type, node_id)

        store_event(topic, data)
