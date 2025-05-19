import asyncio
import json
import logging
import os
from contextlib import AsyncExitStack
from typing import Optional

from aiomqtt import Client, MqttError

from backend.state import AppState
from backend.services.db import (
    insert_node,
    update_nodeinfo,
    update_position,
    get_db_path,
    load_nodes_from_db,
)

logger = logging.getLogger("meshspy.mqtt")

MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.10.202")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "#")


class MQTTService:
    def __init__(self):
        self.nodes: dict[int, dict] = {}
        self.client: Optional[Client] = None
        self._stack = AsyncExitStack()

    async def start(self):
        client_kwargs = {
            "hostname": MQTT_BROKER,
            "port": MQTT_PORT,
        }
        if MQTT_USERNAME and MQTT_PASSWORD:
            client_kwargs["username"] = MQTT_USERNAME
            client_kwargs["password"] = MQTT_PASSWORD

        logger.info(f"🗄️   DB path usato da MQTT: {get_db_path()}")

        try:
            self.client = await self._stack.enter_async_context(Client(**client_kwargs))
            await self.client.subscribe(MQTT_TOPIC)
            logger.info("Sottoscritto a %s", MQTT_TOPIC)
            logger.info("✅ Connessione MQTT avviata con %s:%s", MQTT_BROKER, MQTT_PORT)
            logger.info("In ascolto su topic MQTT")

            # Carica i nodi salvati
            self.nodes = load_nodes_from_db()

            asyncio.create_task(self._listener())
        except MqttError as e:
            logger.error("❌ Errore nella connessione MQTT: %s", e)
            self.stop()

    async def stop(self):
        await self._stack.aclose()
        logger.info("MQTT listener fermato")

    async def _listener(self):
        assert self.client is not None
        try:
            async with self.client.messages() as messages:
                async for msg in messages:
                    await self._handle_message(msg.topic, msg.payload)
        except MqttError as e:
            logger.error("MQTT listener errore: %s", e)

    async def _handle_message(self, topic: str, payload: bytes):
        try:
            decoded = payload.decode("utf-8")
        except UnicodeDecodeError as e:
            logger.warning("Errore decoding UTF-8 del messaggio su %s: %s", topic, e)
            return

        try:
            data = json.loads(decoded)
        except json.JSONDecodeError:
            logger.warning("Errore parsing JSON del messaggio su %s: %s", topic, decoded)
            return

        node_id = data.get("from")
        if not node_id:
            logger.warning("Messaggio senza campo 'from': %s", data)
            return

        if node_id == "Server-MeshSpy":
            return  # ignora i messaggi inviati dal server stesso

        # Se il nodo non è in memoria, registralo
        if node_id not in self.nodes:
            name = data.get("name", f"node-{node_id}")
            insert_node(node_id, name)
            self.nodes[node_id] = {"name": name, "data": {}}
            logger.info("Nuovo nodo rilevato: %s", node_id)

        node = self.nodes[node_id]
        node["data"].update(data)

        if "name" in data:
            update_nodeinfo(node_id, data["name"])
            node["name"] = data["name"]
            logger.info("Aggiornato nodeinfo per %s → %s", node_id, data["name"])

        if "lat" in data and "lon" in data:
            lat, lon = data["lat"], data["lon"]
            prev = node["data"].get("lat"), node["data"].get("lon")
            if (lat, lon) != prev:
                update_position(node_id, lat, lon)
                logger.info("Aggiornata posizione per %s: (%.5f, %.5f)", node_id, lat, lon)

        msg_type = data.get("type", "text")
        if msg_type != "text":
            logger.info("Tipo messaggio sconosciuto (%s) da %s", msg_type, node_id)

    def get_nodes(self):
        return self.nodes

    def send_position_request(self, node_id: int):
        if self.client is None:
            raise RuntimeError("MQTT client non inizializzato")
        topic = f"mesh/request/{node_id}/location"
        payload = json.dumps({"cmd": "request_position", "from": "Server-MeshSpy"})
        asyncio.create_task(self.client.publish(topic, payload))
        logger.info("Comando 'request_position' inviato a %s su topic %s", node_id, topic)


mqtt_service = MQTTService()


def get_mqtt_service():
    return mqtt_service
