import logging
from db_utils import save_command, save_position

def handle_mqtt_message(packet):
    if packet.get("type") == "command":
        save_command(packet)
    elif packet.get("type") == "position":
        save_position(packet)
    else:
        logging.warning(f"Tipo di pacchetto MQTT sconosciuto: {packet.get('type')}")
