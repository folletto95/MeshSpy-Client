import logging
from backend.services.setup_proto import proto_modules

log = logging.getLogger("meshspy.protodecod")

# Alias per comodità
mqtt_pb2 = proto_modules.get("mqtt_pb2")
mesh_pb2 = proto_modules.get("mesh_pb2")


def decode_meshtastic_message(payload_bytes: bytes) -> dict:
    """
    Decodifica un messaggio MQTT Meshtastic da bytes a dizionario leggibile.
    """
    decoded = {}

    try:
        if mqtt_pb2 is None:
            raise ImportError("mqtt_pb2 non disponibile nei proto_modules")

        from_client = mqtt_pb2.ToClient()
        from_client.ParseFromString(payload_bytes)

        decoded["decoded"] = str(from_client)
        decoded["raw"] = payload_bytes.hex()

        if from_client.HasField("nodeInfo"):
            decoded["node_num"] = from_client.nodeInfo.num

    except Exception as e:
        log.warning(f"❌ Errore nel decodificare messaggio MQTT: {e}")
        decoded["error"] = str(e)

    return decoded
