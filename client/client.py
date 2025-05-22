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
from flask import Flask, jsonify
from db_utils import update_node_info, save_packet, init_db

from receive import setup_receive


setup_receive(iface, args.server_url)



DB_FILE = "packets.db"
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "<h1>MeshSpy Client è attivo</h1><p>Usa <a href='/packets'>/packets</a> per i dati.</p>"

@app.route("/packets", methods=["GET"])
def get_all_packets():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, from_node, to_node, message, packet_type, timestamp FROM packets ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
        print(f"[DEBUG] Trovati {len(rows)} pacchetti nel DB.")
        for r in rows:
            print(f"[DEBUG] Pacchetto: {r}")
    return jsonify([
        {"id": r[0], "from": r[1], "to": r[2], "message": r[3], "type": r[4], "timestamp": r[5]} for r in rows
    ])

@app.route("/packets/grouped", methods=["GET"])
def get_packets_grouped():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT from_node, COUNT(*), MAX(timestamp) 
            FROM packets GROUP BY from_node ORDER BY MAX(timestamp) DESC
        """)
        rows = c.fetchall()
    return jsonify([
        {"from": r[0], "count": r[1], "last_seen": r[2]} for r in rows
    ])

def start_web_server():
    app.run(host="0.0.0.0", port=5000)

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

        node = interface.localNode
        user = node.get("user", {}) if isinstance(node, dict) else getattr(node, "user", {})
        long_name = user.get("longName", "N/A")
        short_name = user.get("shortName", "N/A")

        update_node_info(
            node_num=getattr(info, "my_node_num", "N/A"),
            long_name=long_name,
            short_name=short_name,
            hw_model=getattr(info, "hardware_model", "Unknown"),
            firmware_version=getattr(info, "version", "Unknown")
        )
    except Exception as e:
        logging.error(f"[on_connection] Errore: {e}")

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

    pub.subscribe(lambda p, i: on_receive(p, i, args.server_url), "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")
    logging.info("[DEBUG] Subscrizione a 'meshtastic.receive' attiva")

    devPath = args.port
    if args.port is None or args.port == "auto":
        ports = findPorts()
        if not ports:
            logging.error("❌ Nessun dispositivo Meshtastic trovato automaticamente.")
            sys.exit(1)
        devPath = ports[0]
        logging.info(f"[AUTO] Nodo trovato su {devPath}")

    iface = connect_with_retry(devPath)

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
