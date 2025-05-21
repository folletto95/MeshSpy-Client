#!/usr/bin/env python3
"""
Client Meshtastic esteso:
- Salva tutti i pacchetti ricevuti in SQLite
- Espone una pagina web per consultarli
- Permette gestione del nodo
"""

import argparse
import json
import logging
import sqlite3
import time
from threading import Thread

import meshtastic.serial_interface
import requests
from pubsub import pub
from flask import Flask, jsonify

DB_FILE = "packets.db"
app = Flask(__name__)

@app.route("/packets", methods=["GET"])
def get_all_packets():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, from_node, to_node, message, packet_type, timestamp FROM packets ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
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

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_node TEXT,
                to_node TEXT,
                message TEXT,
                packet_type TEXT,
                raw_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_packet(packet):
    raw_json = json.dumps(packet)
    from_node = packet.get("from", "")
    to_node = packet.get("to", "")
    packet_type = packet.get("decoded", {}).get("portnum", "")
    message = packet.get("decoded", {}).get("payload", None)

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO packets (from_node, to_node, message, packet_type, raw_json)
            VALUES (?, ?, ?, ?, ?)
        """, (from_node, to_node, message, packet_type, raw_json))
        conn.commit()

def update_node_info(*args, **kwargs):
    pass  # Placeholder, già definito altrove se serve

def on_receive(packet, interface, server_url):
    logging.info(f"Ricevuto pacchetto: {packet}")
    save_packet(packet)
    try:
        if server_url:
            resp = requests.post(server_url, json=packet)
            resp.raise_for_status()
            logging.info(f"Inoltrato al server: {resp.status_code}")
    except Exception as e:
        logging.error(f"Errore invio al server: {e}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connesso al nodo Meshtastic")
    info = getattr(interface, "myInfo", None)
    if not info:
        logging.warning("Info nodo non disponibile (myInfo is None)")
        return

    node = interface.localNode
    try:
        user = node.get("user", {}) if isinstance(node, dict) else getattr(node, "user", {})
        long_name = user.get("longName", "N/A")
        short_name = user.get("shortName", "N/A")
    except Exception:
        long_name = "Unknown"
        short_name = "??"

    update_node_info(
        node_num=info.my_node_num,
        long_name=long_name,
        short_name=short_name,
        hw_model=info.hardware_model,
        firmware_version=info.version
    )


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

def main():
    parser = argparse.ArgumentParser(description="Client Meshtastic avanzato")
    parser.add_argument("--port", default=None, help="Porta seriale (es. /dev/ttyUSB0)")
    parser.add_argument("--server-url", help="URL per inoltro pacchetti")
    parser.add_argument("--send-text", help="Messaggio da inviare")
    parser.add_argument("--show-info", action="store_true", help="Mostra info nodo")
    parser.add_argument("--set-owner", nargs="+", help="Imposta nome: <long_name> [short_name]")
    parser.add_argument("--web", action="store_true", help="Avvia interfaccia web")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    init_db()

    if args.web:
        t = Thread(target=start_web_server, daemon=True)
        t.start()

    pub.subscribe(lambda p, i: on_receive(p, i, args.server_url), "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    iface = meshtastic.serial_interface.SerialInterface(devPath=args.port)

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
        logging.info("Interrotto")
    finally:
        iface.close()

if __name__ == "__main__":
    main()
