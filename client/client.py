#!/usr/bin/env python3
"""
Script esteso per Raspberry Pi connessa via USB a un nodo Meshtastic.
Permette di inoltrare pacchetti, inviare messaggi e gestire il nodo.
"""
import argparse
import logging
import time
import requests
import meshtastic.serial_interface
from pubsub import pub

def on_receive(packet, interface, server_url):
    logging.info(f"Ricevuto pacchetto: {packet}")
    try:
        if server_url:
            resp = requests.post(server_url, json=packet)
            resp.raise_for_status()
            logging.info(f"Inoltrato al server con status {resp.status_code}")
    except Exception as e:
        logging.error(f"Errore invio al server: {e}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connesso al dispositivo Meshtastic")

def print_node_info(iface):
    info = iface.myInfo
    print("=== Informazioni Nodo ===")
    print(f"Nome lungo: {iface.localNode.getLongName()}")
    print(f"Nome corto: {iface.localNode.getShortName()}")
    print(f"Numero nodo: {info.my_node_num}")
    print(f"Versione firmware: {info.version}")
    print(f"Model: {info.hardware_model}")

def set_owner_name(iface, long_name, short_name=None):
    iface.localNode.setOwner(long_name, short_name)
    print(f"Nome utente impostato a: {long_name} ({short_name})" if short_name else long_name)

def main():
    parser = argparse.ArgumentParser(description="Meshtastic client tool")
    parser.add_argument("--port", default=None, help="Porta seriale (es. /dev/ttyUSB0)")
    parser.add_argument("--server-url", help="Endpoint HTTP per inoltro pacchetti")
    parser.add_argument("--send-text", help="Messaggio da inviare")
    parser.add_argument("--show-info", action="store_true", help="Mostra informazioni sul nodo")
    parser.add_argument("--set-owner", nargs="+", help="Imposta nome utente: <long_name> [short_name]")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    pub.subscribe(lambda p, i: on_receive(p, i, args.server_url), "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    iface = meshtastic.serial_interface.SerialInterface(devPath=args.port)

    try:
        if args.send_text:
            iface.sendText(args.send_text)
            logging.info(f"Messaggio inviato: {args.send_text}")

        if args.show_info:
            print_node_info(iface)

        if args.set_owner:
            long_name = args.set_owner[0]
            short_name = args.set_owner[1] if len(args.set_owner) > 1 else None
            set_owner_name(iface, long_name, short_name)

        if not (args.send_text or args.show_info or args.set_owner):
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Terminazione su richiesta")
    finally:
        iface.close()

if __name__ == "__main__":
    main()
