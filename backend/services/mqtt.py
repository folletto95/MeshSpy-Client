import asyncio
import logging
import os
from typing import Optional
import paho.mqtt.client as mqtt
from google.protobuf.json_format import MessageToDict
from backend.services import protodecod, state
from backend.services.log_stream import log_stream_manager

logger = logging.getLogger("meshspy.mqtt")

VERBOSE = os.environ.get("VERBOSE_LOGGING", "0") == "1"

class MQTTService:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.state = GlobalState()
        self.db = NodeDatabase()
        self.reconnect_delay = 3

    def start(self):
        asyncio.create_task(self._listener())

    async def _listener(self):
        while True:
            try:
                logger.info("⚙️  Avvio tentativo connessione MQTT...")
                self.client = mqtt.Client()
                self.client.on_connect = self._on_connect
                self.client.on_message = self._on_message
                self.client.connect(self.state.mqtt_broker, self.state.mqtt_port, 60)
                self.client.loop_start()
                logger.info("📡 Client MQTT creato, in attesa di connessione...")
                break
            except Exception as e:
                logger.error(f"❌ Errore nella connessione MQTT: {e}")
                logger.info(f"Ritento la connessione MQTT tra {self.reconnect_delay} secondi...")
                await asyncio.sleep(self.reconnect_delay)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ Connessione MQTT stabilita!")
            topic = self.state.mqtt_topic
            self.client.subscribe(topic)
            logger.info(f"🔔 Iscritto al topic: {topic}")
        else:
            logger.error(f"❌ Connessione MQTT fallita con codice: {rc}")

    def _on_message(self, client, userdata, msg):
        asyncio.create_task(self._handle_message(msg.topic, msg.payload))

    async def _handle_message(self, topic, payload):
        try:
            decoded_str = payload.decode("utf-8")
            if VERBOSE:
                logger.debug(f"📩 Payload UTF-8 ricevuto da {topic}: {decoded_str}")
        except UnicodeDecodeError as e:
            logger.warning(f"Errore decoding UTF-8 del messaggio su {topic}: {e}")

        try:
            envelope = protodecod.decode_protobuf(payload)
            if envelope is None or not envelope.packet:
                logger.debug("⚠️  Envelope o packet mancante, salto messaggio.")
                return

            packet = envelope.packet
            decoded = MessageToDict(packet, preserving_proto_field_name=True)

            # Verifica campo 'id'
            if "id" not in decoded:
                logger.warning("⚠️  Nessun campo 'id' trovato in decoded.packet")
                return

            node_id = packet.from_
            node_sender = topic.split("/")[-1]

            node_data = {
                "from": node_id,
                "sender": node_sender,
                "to": packet.to,
                "id": packet.id,
                "channel": packet.channel,
                "timestamp": packet.timestamp,
                "hop_start": packet.hop_start,
                "hops_away": packet.hops_away,
                "type": packet.decoded.WhichOneof("payload") if packet.HasField("decoded") else "",
            }

            # Inserimento payload decodificato
            if packet.HasField("decoded"):
                payload_type = packet.decoded.WhichOneof("payload")
                if payload_type:
                    payload_dict = MessageToDict(getattr(packet.decoded, payload_type), preserving_proto_field_name=True)
                    node_data["payload"] = payload_dict

            # Metadati
            if packet.HasField("rx_meta"):
                rx = packet.rx_meta
                node_data["rssi"] = rx.rssi
                node_data["snr"] = rx.snr

            if VERBOSE:
                logger.debug(f"✅ Packet decodificato: {node_data}")
            # Salva nodo
            self._db.save_node(node_data)
            logger.info(f"📨  Messaggio valido da {node_id}: {node_data}")

        except UnicodeDecodeError as e:
            logger.warning(f"Errore decoding UTF-8 del messaggio su {topic}: {e}")
        except Exception as e:
            logger.warning(f"⚠️  Errore durante la decodifica protobuf: {e}")

    def stop(self):
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("📴 Disconnessione MQTT completata")


mqtt_service = MQTTService()


def get_mqtt_service() -> MQTTService:
    return mqtt_service
