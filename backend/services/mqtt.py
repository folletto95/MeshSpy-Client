import asyncio
import logging
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Dict

from pydantic import BaseModel, ValidationError
from dotenv import find_dotenv, load_dotenv
from aiomqtt import Client, MqttError

from backend.logging_config import logger
from backend.services.db import (
    register_node,
    upsert_nodeinfo,
    update_position,
    store_event,
)

class NodeData(BaseModel):
    name: str
    data: dict

logger = logging.getLogger("meshspy.mqtt")

env_path = find_dotenv(usecwd=True)
if not env_path:
    raise RuntimeError(".env non trovato: mettilo nella radice di MeshSpy")
load_dotenv(env_path)

BROKER_HOST     = os.getenv("MQTT_HOST", "192.168.10.202")
BROKER_PORT     = int(os.getenv("MQTT_PORT", 1883))
BROKER_USERNAME = os.getenv("MQTT_USERNAME", "")
BROKER_PASSWORD = os.getenv("MQTT_PASSWORD", "")
TOPICS          = os.getenv("MQTT_TOPICS", "#").split(",")

logger.debug("Caricate da .env: HOST=%s PORT=%s USER=%r", BROKER_HOST, BROKER_PORT, BROKER_USERNAME)

class MQTTService:
    def __init__(self) -> None:
        logger.info(f"🗄️  DB path usato da MQTT: ~/.meshspy_data/node.db")
        self._stack: AsyncExitStack | None = None
        self.client: Client | None = None
        self.name_map: Dict[str, str] = {}
        self.nodes: Dict[str, NodeData] = {}

    async def start(self) -> None:
        self._stack = AsyncExitStack()
        try:
            client_kwargs: dict[str, Any] = {
                "hostname": BROKER_HOST,
                "port": BROKER_PORT,
            }
            if BROKER_USERNAME:
                client_kwargs["username"] = BROKER_USERNAME
                client_kwargs["password"] = BROKER_PASSWORD

            self.client = await self._stack.enter_async_context(Client(**client_kwargs))

            for topic in TOPICS:
                await self.client.subscribe(topic)
                logger.info("Sottoscritto a %s", topic)

            logger.info("✅ Connessione MQTT avviata con %s:%s", BROKER_HOST, BROKER_PORT)
            logger.info("In ascolto su topic MQTT")
            asyncio.create_task(self._listener(self.client.messages))

        except MqttError as e:
            logger.error("❌ Errore MQTT: %s", e)
            await self.stop()
            raise

    async def _listener(self, messages) -> None:
        async for msg in messages:
            await self._handle_message(msg.topic, msg.payload)

    async def stop(self) -> None:
        if self._stack:
            await self._stack.aclose()
            logger.info("MQTT listener fermato")

    async def _handle_message(self, topic: Any, payload: bytes) -> None:
        topic_str = str(topic)

        try:
            payload_str = payload.decode("utf-8")
        except UnicodeDecodeError as e:
            logger.warning("Errore decoding UTF-8 del messaggio su %s: %s", topic_str, e)
            return

        try:
            data = json.loads(payload_str)
        except json.JSONDecodeError as e:
            logger.warning("Errore nel parsing JSON del messaggio MQTT su %s: %s", topic_str, e)
            return

        if "from" not in data:
            logger.warning("Messaggio senza campo 'from': %s", data)
            return
        node_id = str(data["from"])
        name = self.name_map.get(node_id, node_id)
        self.nodes[node_id] = NodeData(name=name, data=data)

        # Salva/aggiorna info nodo
        node_id = data.get("from")
        name = self.name_map.get(node_id, node_id)
        register_node(node_id, name)

        # Gestione messaggi di posizione
        if "position" in data:
            pos = data["position"]
            lat, lon = pos.get("latitude"), pos.get("longitude")

            if lat is not None and lon is not None:
                old_data = self.nodes.get(node_id)
                old_pos = old_data.data.get("position", {}) if old_data else {}
                old_lat, old_lon = old_pos.get("latitude"), old_pos.get("longitude")

                if (lat != old_lat) or (lon != old_lon):
                    logger.info("Posizione aggiornata per %s → lat: %.5f, lon: %.5f", name, lat, lon)
                    update_position(node_id, lat, lon)
                else:
                    logger.debug("Posizione invariata per %s, non aggiorno DB", name)

        # Gestione nodeinfo
        if "user" in data:
            user = data["user"]
            short_name = user.get("shortName")
            long_name = user.get("longName")

            if short_name:
                self.name_map[node_id] = short_name
                logger.info("Aggiornato nodeinfo per %s → %s", node_id, short_name)
            elif long_name:
                self.name_map[node_id] = long_name
                logger.info("Aggiornato nodeinfo per %s → %s", node_id, long_name)

        # Gestione comandi
        if "cmd" in data:
            logger.info("Ricevuto comando da %s: %s", name, data["cmd"])
            store_event(node_id, f"cmd: {data['cmd']}")


mqtt_service = MQTTService()

def get_mqtt_service() -> MQTTService:
    return mqtt_service
