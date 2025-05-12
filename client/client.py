#!/usr/bin/env python3
"""
Script per Raspberry Pi che si connette a un nodo Meshtastic via USB e inoltra i dati ricevuti a un server HTTP.
"""
import argparse
import logging
import time
import requests
import meshtastic.serial_interface
from pubsub import pub

def on_receive(packet, interface, server_url):
    """
    Callback chiamato ad ogni pacchetto ricevuto.
    Invia il pacchetto al server in formato JSON.
    """
    logging.info(f"Ricevuto pacchetto: {packet}")
    try:
        resp = requests.post(server_url, json=packet)
        resp.raise_for_status()
        logging.info(f"Inoltrato al server con status {resp.status_code}")
    except Exception as e:
        logging.error(f"Errore invio al server: {e}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    """
    Callback chiamato alla (ri)connessione al dispositivo.
    """
    logging.info("Connesso al dispositivo Meshtastic")

def main():
    parser = argparse.ArgumentParser(
        description="Meshtastic to Server forwarder"
    )
    parser.add_argument(
        "--port", default=None,
        help="Serial port del dispositivo Meshtastic (es. /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--server-url", required=True,
        help="URL dell'endpoint server per POST dei dati"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Sottoscrizione ai topic Meshtastic
    pub.subscribe(
        lambda packet, interface: on_receive(packet, interface, args.server_url),
        "meshtastic.receive"
    )
    pub.subscribe(on_connection, "meshtastic.connection.established")

    # Connessione al dispositivo
    interface = meshtastic.serial_interface.SerialInterface(devPath=args.port)

    try:
        # Loop infinito, i callback gestiscono i dati
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Terminazione script su richiesta utente")
    finally:
        interface.close()

if __name__ == "__main__":
    main()
