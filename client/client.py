#!/usr/bin/env python3
import argparse
import json
import logging
import sqlite3
import sys
import time
from threading import Thread

import meshtastic.serial_interface
import requests
from meshtastic.util import findPorts
from pubsub import pub
from flask import Flask
from rest_api import start_web_server
from db_utils import update_node_info, save_packet, init_db
from receive import setup_receive  # Nuovo modulo separato

DB_FILE = "packets.db"
app = Flask(__name__)

def print_node_info(iface):
    info = iface.myInfo
    print("=== Info Nodo ===")
    print(f"Nome lungo: {iface.localNode.getLongName()}")
    print(f"Nome corto: {iface.localNode.getShortName()}")
    print(f"Numero nodo: {info.my_node_num}")
    print(f"Versione firmware: {info.version}")
    print(f"Modello HW: {info.hardware_model}")

def set_owner_name(iface, long_name, short_name=None):
    iface.localNode.setOwner(long_name, short_name)
    print(f"Nome utente impostato a: {long_name} ({short_name})" if short_name else long_name)

def connect_with_retry(devPath, max_attempts=5, delay=5):
    attempt = 0
    while attempt < max_attempts:
        try:
            logging.info(f"[Tentativo {attempt+1}/{max_attempts}] Connessione al nodo su {devPath}...")
            iface = meshtastic.serial_interface.SerialInterface(devPath=devPath)
            return iface
        except Exception as e:
            logging.warning(f"Connessione fallita: {e}")
            attempt += 1
            time.sleep(delay)
    logging.error("❌ Impossibile connettersi al nodo Meshtastic dopo vari tentativi.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Client Meshtastic avanzato")
    parser.add_argument("--port", default=None, help="Porta seriale o 'auto'")
    parser.add_argument("--server-url", help="URL per inoltro pacchetti")
    parser.add_argument("--send-text", help="Messaggio da inviare")
    parser.add_argument("--show-info", action="store_true", help="Mostra info nodo")
    parser.add_argument("--set-owner", nargs="+", help="Imposta nome: <long_name> [short_name]")
    parser.add_argument("--web", action="store_true", help="Avvia interfaccia web")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    init_db()

    if args.web:
        Thread(target=start_web_server, daemon=True).start()

    devPath = args.port
    if args.port is None or args.port == "auto":
        ports = findPorts()
        if not ports:
            logging.error("❌ Nessun dispositivo Meshtastic trovato automaticamente.")
            sys.exit(1)
        devPath = ports[0]
        logging.info(f"[AUTO] Nodo trovato su {devPath}")

    iface = connect_with_retry(devPath)

    setup_receive(iface, args.server_url)

    try:
        if args.send_text:
            iface.sendText(args.send_text)
            logging.info(f"Inviato: {args.send_text}")
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
        logging.info("Interrotto da tastiera")
    finally:
        iface.close()

if __name__ == "__main__":
    main()
