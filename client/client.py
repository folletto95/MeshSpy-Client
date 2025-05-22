import os
import sys
import time
import argparse
import logging
from dotenv import load_dotenv

import meshtastic
import meshtastic.serial_interface
from pubsub import pub

from db_utils import init_db
from rest_api import start_flask_server
from receive import on_receive, on_connection
from mqtt_handler import start_mqtt_client
from meshtastic_utils import auto_detect_port
from interface_setup import connect_interface

logging.basicConfig(level=logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Serial port del dispositivo Meshtastic")
    parser.add_argument("--web", action="store_true", help="Avviare anche l'interfaccia web Flask")
    parser.add_argument("--mqtt", action="store_true", help="Attiva comunicazione MQTT")
    return parser.parse_args()

def main():
    args = parse_args()

    # Caricamento variabili da .env se presente
    load_dotenv()

    # Inizializza DB
    init_db()

    # Rilevamento porta automatica se non specificata
    devPath = args.port or auto_detect_port()
    if not devPath:
        logging.error("Nessuna porta seriale trovata. Controlla il collegamento del nodo.")
        sys.exit(1)

    # Connessione al nodo Meshtastic con retry
    iface = connect_interface(devPath)
    if not iface:
        logging.error("Impossibile connettersi al nodo Meshtastic.")
        sys.exit(1)

    # Abbonamento eventi pubsub
    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    # Opzionale: avvio server Flask
    if args.web:
        start_flask_server()

    # Opzionale: avvio client MQTT
    if args.mqtt:
        mqtt_config = {
            "broker_host": os.getenv("MQTT_BROKER_HOST", "localhost"),
            "broker_port": int(os.getenv("MQTT_BROKER_PORT", 1883)),
            "username": os.getenv("MQTT_USERNAME"),
            "password": os.getenv("MQTT_PASSWORD"),
            "topic_prefix": os.getenv("MQTT_TOPIC_PREFIX", "msh"),
        }
        start_mqtt_client(iface.myInfo.my_node_num, **mqtt_config)

    # Ciclo infinito per tenere il programma attivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Terminazione richiesta dall'utente.")
        iface.close()

if __name__ == "__main__":
    main()
