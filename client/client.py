#!/usr/bin/env python3
"""
Client Meshtastic + MQTT
- Salva pacchetti
- Interfaccia Web REST
- Pubblica su MQTT
- Riceve comandi MQTT
"""

import argparse
import json
import logging
import os
import sqlite3
import subprocess
import time
from threading import Thread

import meshtastic.serial_interface
import paho.mqtt.client as mqtt
import requests
from flask import Flask, jsonify, render_template
from pubsub import pub

from dotenv import load_dotenv

load_dotenv()

DB_FILE = "packets.db"
app = Flask(__name__, template_folder="templates")

mqtt_client = None
mqtt_config = {}

# === Flask Endpoints ===
@app.route("/")
def index():
    return render_template("index.html")

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
        c.execute("SELECT from_node, COUNT(*), MAX(timestamp) FROM packets GROUP BY from_node ORDER BY MAX(timestamp) DESC")
        rows = c.fetchall()
    return jsonify([
        {"from": r[0], "count": r[1], "last_seen": r[2]} for r in rows
    ])

def start_web_server():
    app.run(host="0.0.0.0", port=5000)

# === SQLite ===
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

# === MQTT ===
def on_mqtt_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        cmd = payload.get("cmd")
        logging.info(f"MQTT cmd ricevuto: {cmd} -> {payload}")

        if cmd == "update":
            subprocess.run(["./berry-update.sh"], check=False)

        elif cmd == "reboot":
            subprocess.run(["reboot"], check=False)

        elif cmd == "set-position":
            lat = payload.get("lat")
            lng = payload.get("lng")
            if lat is not None and lng is not None:
                logging.info(f"Set GPS: {lat}, {lng}")
                # Simulazione: implementa update nel nodo se necessario
    except Exception as e:
        logging.error(f"Errore nel parsing comando MQTT: {e}")

def start_mqtt_client(node_id, host, port, topic_base, user=None, password=None):
    global mqtt_client
    mqtt_client = mqtt.Client()
    if user and password:
        mqtt_client.username_pw_set(user, password)

    mqtt_client.on_message = on_mqtt_message
    mqtt_client.connect(host, int(port), 60)
    mqtt_client.loop_start()

    command_topic = f"{topic_base}/{node_id}/commands"
    mqtt_client.subscribe(command_topic)
    logging.info(f"MQTT sottoscritto a: {command_topic}")

def publish_packet_mqtt(packet, node_id, topic_base):
    if mqtt_client:
        mqtt_client.publish(f"{topic_base}/{node_id}/packets", json.dumps(packet))

# === Meshtastic ===
def on_receive(packet, interface, server_url):
    logging.info(f"Ricevuto pacchetto: {packet}")
    save_packet(packet)
    publish_packet_mqtt(packet, interface.myInfo.my_node_num, mqtt_config.get("topic_base", "msh/EU_868"))

    try:
        if server_url:
            resp = requests.post(server_url, json=packet)
            resp.raise_for_status()
    except Exception as e:
        logging.error(f"Errore invio al server HTTP: {e}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connesso al nodo Meshtastic")

# === Main ===
def main():
    parser = argparse.ArgumentParser(description="Client Meshtastic avanzato + MQTT")
    parser.add_argument("--port", default=None)
    parser.add_argument("--server-url")
    parser.add_argument("--send-text")
    parser.add_argument("--show-info", action="store_true")
    parser.add_argument("--set-owner", nargs="+")
    parser.add_argument("--web", action="store_true")

    parser.add_argument("--mqtt-host")
    parser.add_argument("--mqtt-port", default=1883)
    parser.add_argument("--mqtt-topic", default="msh/EU_868")
    parser.add_argument("--mqtt-user")
    parser.add_argument("--mqtt-password")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    init_db()

    if args.web:
        t = Thread(target=start_web_server, daemon=True)
        t.start()

    iface = meshtastic.serial_interface.SerialInterface(devPath=args.port)

    pub.subscribe(lambda p, i: on_receive(p, i, args.server_url), "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    if args.mqtt_host:
        mqtt_config.update({
            "host": args.mqtt_host,
            "port": args.mqtt_port,
            "topic_base": args.mqtt_topic,
            "user": args.mqtt_user,
            "password": args.mqtt_password,
        })
        start_mqtt_client(iface.myInfo.my_node_num, args.mqtt_host, args.mqtt_port, args.mqtt_topic, args.mqtt_user, args.mqtt_password)

    try:
        if args.send_text:
            iface.sendText(args.send_text)
        if args.show_info:
            print(f"Node: {iface.myInfo.my_node_num}")
        if args.set_owner:
            long_name = args.set_owner[0]
            short_name = args.set_owner[1] if len(args.set_owner) > 1 else None
            iface.localNode.setOwner(long_name, short_name)

        if not (args.send_text or args.show_info or args.set_owner):
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrotto da utente")
    finally:
        iface.close()

if __name__ == "__main__":
    main()
