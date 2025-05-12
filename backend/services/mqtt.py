# backend/services/mqtt.py

import asyncio
import logging
import json
import os
from contextlib import AsyncExitStack
from typing import Any, Dict

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

            logger.info("In ascolto su topic MQTT")
            asyncio.create_task(self._listener(self.client.messages))

        except MqttError as e:
            logger.error("Errore MQTT in start(): %s", e)
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
            data = json.loads(payload_str)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.warning("Errore nel parsing del messaggio MQTT su %s: %s", topic_str, e)
            return

        node_id = data.get("from")
        if not node_id:
            logger.warning("Messaggio senza campo 'from': %s", payload_str)
            return

        if node_id not in self.nodes:
            logger.info("Nuovo nodo rilevato: %s", node_id)
            register_node(node_id, node_id)
            self.name_map[node_id] = node_id

        msg_type = data.get("type")
        payload_obj = data.get("payload", {})

        if msg_type == "sendtext":
            logger.info("Messaggio testo da %s a %s: %s", node_id, data.get("to"), payload_obj)

        elif msg_type == "sendposition":
            try:
                lat = payload_obj["latitude_i"] / 1e7
                lon = payload_obj["longitude_i"] / 1e7
                update_position(node_id, lat, lon)
                logger.info("Posizione aggiornata per %s: lat=%s lon=%s", node_id, lat, lon)
            except (KeyError, TypeError):
                logger.warning("Dati posizione non validi da %s: %s", node_id, payload_obj)

        elif msg_type == "telemetry":
            logger.info("Telemetria da %s: %s", node_id, payload_obj)

        elif msg_type == "nodeinfo":
            short = payload_obj.get("shortname", "")
            longn = payload_obj.get("longname", "")
            upsert_nodeinfo(node_id, short, longn, node_id)
            realname = longn or short or node_id
            self.name_map[node_id] = realname
            logger.info("Aggiornato nodeinfo per %s → %s", node_id, realname)

        elif msg_type == "waypoint":
            try:
                lat = payload_obj["latitude_i"] / 1e7
                lon = payload_obj["longitude_i"] / 1e7
                logger.info("Waypoint da %s: %s (%s, %s)", node_id, payload_obj.get("name"), lat, lon)
            except (KeyError, TypeError):
                logger.warning("Dati waypoint non validi da %s: %s", node_id, payload_obj)

        elif msg_type == "neighborinfo":
            neighbors = payload_obj.get("neighbors", [])
            logger.info("Nodi vicini visti da %s: %s", node_id, neighbors)

        elif msg_type == "traceroute":
            route = payload_obj.get("route", [])
            logger.info("Traceroute da %s: %s", node_id, route)

        elif msg_type == "detectionsensor":
            logger.info("Rilevamento da sensore %s: %s", payload_obj.get("sensor_type"), payload_obj.get("value"))

        elif msg_type == "paxcounter":
            logger.info("PAX da %s: Wi-Fi=%s BLE=%s", node_id, payload_obj.get("wifi_count"), payload_obj.get("ble_count"))

        elif msg_type == "remotehardware":
            logger.info("Comando hardware remoto da %s: %s su %s", node_id, payload_obj.get("command"), payload_obj.get("target"))

        else:
            logger.info("Tipo messaggio sconosciuto (%s) da %s", msg_type, node_id)

        store_event(node_id, msg_type or topic_str.rsplit("/", 1)[-1], payload_str)


        old_data = self.nodes.get(node_id, {})
        preserved = old_data.get() if old_data else {}
        preserved_fields = {k: preserved[k] for k in ("lat", "lon") if k in preserved}

        if node_id not in self.nodes:
            self.nodes[node_id] = NodeData()

        update_fields = {
            "type": msg_type,
            "payload": payload_obj
        }
        if node_id not in self.nodes:
            self.nodes[node_id] = NodeData()

        update_fields = {
            "type": msg_type,
            "payload": payload_obj
        }
        if msg_type == "sendposition" and 'latitude_i' in payload_obj and 'longitude_i' in payload_obj:
            update_fields["lat"] = payload_obj["latitude_i"] / 1e7
            update_fields["lon"] = payload_obj["longitude_i"] / 1e7

        # Preserva lat/lon esistenti
        preserved = self.nodes[node_id].get()
        for k in ("lat", "lon"):
            if k in preserved and k not in update_fields:
                update_fields[k] = preserved[k]

        self.nodes[node_id].update(update_fields)

async def get_mqtt_service() -> MQTTService:
    return mqtt_service

mqtt_service = MQTTService()
