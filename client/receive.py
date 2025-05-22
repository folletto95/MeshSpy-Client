
import logging
from pubsub import pub
from db_utils import store_packet

def on_receive(packet, interface):
    logging.debug("=== Pacchetto ricevuto ===")
    logging.debug(packet)

    try:
        store_packet(packet)
    except Exception as e:
        logging.error(f"Errore salvataggio pacchetto: {e}")

def setup_receive(iface, server_url=None):
    pub.subscribe(on_receive, "meshtastic.receive")
    logging.debug("[SUBSCRIBE] Registrato on_receive a 'meshtastic.receive'")
