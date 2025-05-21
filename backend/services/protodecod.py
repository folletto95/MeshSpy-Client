import logging
from backend.services.setup_proto import proto_modules

log = logging.getLogger("meshspy.protodecod")

# Alias utili
mqtt_pb2 = proto_modules["mqtt_pb2"]
mesh_pb2 = proto_modules["mesh_pb2"]

def decode_meshtastic_message(payload_bytes: bytes) -> dict:
    """Decodifica un messaggio MQTT Meshtastic da bytes a dict leggibile"""
    decoded = {}

    try:
        from_client = mqtt_pb2.ToClient()
        from_client.ParseFromString(payload_bytes)

        decoded["decoded"] = from_client.__str__()
        decoded["raw"] = payload_bytes.hex()

        # Esempio: accediamo a un campo specifico se esiste
        if from_client.HasField("nodeInfo"):
            decoded["node_num"] = from_client.nodeInfo.num

    except Exception as e:
        log.warning(f"❌ Errore nel decodificare messaggio MQTT: {e}")
        decoded["error"] = str(e)

    return decoded
