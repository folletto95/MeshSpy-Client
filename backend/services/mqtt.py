import asyncio
import json
import logging
import os
from collections import defaultdict
from contextlib import AsyncExitStack
from typing import Optional

from aiomqtt import Client, MqttError
from fastapi import Depends
from dotenv import load_dotenv  # ✅ assicurati di caricare .env

from backend.services.db import (
    init_db,
    insert_node,
    load_nodes_from_db,
    update_position,
    update_nodeinfo,
    get_db_path,
)
from backend.state import AppState

# Carica le variabili da .env
load_dotenv()

logger = logging.getLogger("meshspy.mqtt")

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "#")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

class NodeData:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

class MQTTService:
    def __init__(self):
        self.client: Optional[Client] = None
        self.stack: Optional[AsyncExitStack] = None
        self.nodes = {}
        self.nodes_by_id = {}
        self.state = AppState()
        self.db_path = get_db_path()
        self.my_node_id = "Server-MeshSpy"

    async def start(self):
        logger.info("🗄️   DB path usato da MQTT: %s", self.db_path)
        init_db()
        self.nodes = {}

        self.stack = AsyncExitStack()
        await self.stack.__aenter__()

        self.client = await self.stack.enter_async_context(
            Client(
                hostname=MQTT_HOST,
                port=MQTT_PORT,
                username=MQTT_USERNAME if MQTT_USERNAME else None,
                password=MQTT_PASSWORD if MQTT_PASSWORD else None,
                keepalive=60,
            )
        )

        await self.client.subscribe(MQTT_TOPIC)
        logger.info("Sottoscritto a %s", MQTT_TOPIC)
        logger.info("✅ Connessione MQTT avviata con %s:%s", MQTT_HOST, MQTT_PORT)
        logger.info("In ascolto su topic MQTT")

        asyncio.create_task(self._listener())

    async def stop(self):
        logger.info("MQTT listener fermato")
        if self.stack:
            await self.stack.aclose()

    async def _listener(self):
        assert self.client is not None
        try:
            messages = self.client.messages  # NON usare async with
            async for msg in messages:
                await self._handle_message(msg.topic, msg.payload)
        except MqttError as e:
            logger.error("MQTT listener error: %s", e)
        finally:
            await self.stop()

    async def _handle_message(self, topic, payload):
        try:
            decoded = payload.decode("utf-8")
            logger.info("📩 Payload ricevuto (UTF-8): %s", decoded)
            message = json.loads(decoded)
        except UnicodeDecodeError as e:
            logger.warning("Errore decoding UTF-8 del messaggio su %s: %s", topic, e)
            logger.warning("📦 Payload raw: %s", payload)
            return
        except json.JSONDecodeError as e:
            logger.warning("Errore decoding JSON del messaggio su %s: %s", topic, e)
            logger.warning("📄 Payload UTF-8: %s", decoded)
            return

        node_id = str(message.get("from"))
        if not node_id:
            logger.warning("Messaggio senza campo 'from': %s", message)
            return

        if node_id == self.my_node_id:
            return

        if "cmd" in message:
            logger.debug("🔁 Ignorato messaggio 'cmd' da %s: %s", node_id, message["cmd"])
            return

        logger.info("📨 Messaggio valido da %s: %s", node_id, message)
        self.nodes[node_id] = NodeData(name=node_id, data=message)

def get_mqtt_service() -> MQTTService:
    return AppState().mqtt_service

mqtt_service = get_mqtt_service()
