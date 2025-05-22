import logging
import json
import requests
from pubsub import pub
from db_utils import save_packet_to_db

iface = None

def set_interface(interface):
    global iface
    iface = interface

def set_node_position(lat, lng):
    if iface:
        logging.info(f"Aggiorno posizione nodo: lat={lat}, lng={lng}")
        iface.localNode.setPosition(lat=lat, lon=lng)

def on_receive(packet, interface, server_url):
    logging.info("[DEBUG] on_receive invocato")
    logging.info(f"[RECEIVE] Packet: {json.dumps(packet, indent=2)}")
    try:
        save_packet(packet)
        if server_url:
            resp = requests.post(server_url, json=packet)
            resp.raise_for_status()
            logging.info(f"Inoltrato al server: {resp.status_code}")
    except Exception as e:
        logging.warning(f"[on_receive] Errore: {e}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connesso al nodo Meshtastic")
    try:
        interface.showInfo()
    except Exception as e:
        logging.warning(f"[on_connection] showInfo fallito: {e}")
    try:
        info = getattr(interface, "myInfo", None)
        logging.info(f"[DEBUG] myInfo: {info}")
        logging.info(f"[DEBUG] iface.nodes: {interface.nodes}")
        logging.info(f"[DEBUG] iface.localNode: {interface.localNode}")
        if not info:
            logging.warning("Info nodo non disponibile (myInfo is None)")
            return
    except Exception as e:
        logging.warning(f"[on_connection] eccezione durante accesso alle info nodo: {e}")
