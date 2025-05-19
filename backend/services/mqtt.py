import asyncio
import json
import logging
import os
from collections import defaultdict
from contextlib import AsyncExitStack
from typing import Optional

from aiomqtt import Client, MqttError
from fastapi import Depends
from dotenv import load_dotenv

from backend.services.db import (
    init_db,
    get_db_path,
    load_nodes_as_dict,
)
from backend.services.message_handler import insert_or_update_node_from_message
from backend.state import AppState
from backend.metrics import messages_received

# Carica le variabili da .env
load_dotenv()

logger = logging.getLogger("meshspy.mqtt")

MQTT_HOST = os.getenv("MQTT_HOST")
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
        self.nodes = AppState().nodes
        self.nodes_by_id = {}
        self.state = AppState()
        self.db_path = get_db_path()
        self.my_node_id = "Server-MeshSpy"

    async def start(self):
        logger.info("🗄️   DB path usato da MQTT: %s", self.db_path)
        init_db()
        self.nodes.update(load_nodes_as_dict())

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
            messages = self.client.messages
            async for msg in messages:
                await self._handle_message(msg.topic, msg.payload)
        except Exception as e:
            logger.exception("❌ Errore durante connessione MQTT")

            # Rilancia per segnalare fallimento
            raise
            logger.error("MQTT listener error: %s", e)
        finally:
            await self.stop()

    async def _handle_message(self, topic, payload):
        try:
            decoded = payload.decode("utf-8")
            logger.info("📩 Payload ricevuto (UTF-8): %s", decoded)
            message = json.loads(decoded)
            messages_received.inc()
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

        # Recupera dati precedenti se esistono
        old_data = self.nodes.get(node_id)
        merged_data = old_data.data.copy() if old_data else {}

        # Aggiorna solo i campi presenti nel nuovo messaggio
        for key, value in message.items():
            if value is not None:
                merged_data[key] = value

        self.nodes[node_id] = NodeData(name=node_id, data=merged_data)

        insert_or_update_node_from_message(message)

def get_mqtt_service() -> MQTTService:
    return AppState().mqtt_service

async def test_publish(self, topic="test/topic", payload="MQTT test da MeshSpy"):
    if self.client:
        await self.client.publish(topic, payload)
        logger.info(f"📤 Messaggio MQTT inviato su '{topic}': '{payload}'")
    else:
        logger.error("❌ MQTT non connesso, impossibile inviare il messaggio.")

mqtt_service = get_mqtt_service()