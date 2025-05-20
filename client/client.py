#!/usr/bin/env python3
"""

Client Meshtastic con supporto MQTT e REST
- Usa moduli esterni per database, MQTT, REST, Meshtastic
"""

import argparse
import logging
import os
import time
from threading import Thread

import meshtastic.serial_interface
from pubsub import pub
from dotenv import load_dotenv
import requests

from db_utils import init_db, save_packet, update_node_info
from mqtt_handler import start_mqtt_client, publish_packet_mqtt
from meshtastic_utils import set_interface
from rest_api import app as rest_app

load_dotenv()

mqtt_config = {}

def start_web_server():
    rest_app.run(host="0.0.0.0", port=5000)

def on_receive(packet, interface, server_url):
    logging.info(f"Ricevuto pacchetto: {packet}")
    save_packet(packet)
    publish_packet_mqtt(packet, interface.myInfo.my_node_num, mqtt_config.get("topic_base", "msh/EU_868"))
    try:
        if server_url:
            resp = requests.post(server_url, json=packet)
            resp.raise_for_status()
    except Exception as e:
        logging.error(f"Errore HTTP: {e}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connesso al nodo Meshtastic")
    info = interface.myInfo
    node = interface.localNode
    user = node.user
    update_node_info(
        node_num=info.my_node_num,
        long_name=user.get("longName", "N/A"),
        short_name=user.get("shortName", "N/A"),
        hw_model=info.hardware_model,
        firmware_version=info.version
    )

def main():
    parser = argparse.ArgumentParser(description="Client Meshtastic avanzato + MQTT")
    parser.add_argument("--port", default=None)
    parser.add_argument("--server-url")
    parser.add_argument("--send-text")
    parser.add_argument("--show-info", action="store_true")
    parser.add_argument("--set-owner", nargs="+")
    parser.add_argument("--web", action="store_true")

    parser.add_argument("--mqtt-host", default=os.getenv("MQTT_HOST"))
    parser.add_argument("--mqtt-port", default=os.getenv("MQTT_PORT", "1883"))
    parser.add_argument("--mqtt-topic", default=os.getenv("MQTT_TOPIC", "msh/EU_868"))
    parser.add_argument("--mqtt-user", default=os.getenv("MQTT_USER"))
    parser.add_argument("--mqtt-password", default=os.getenv("MQTT_PASSWORD"))

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    init_db()

    if args.web:
        Thread(target=start_web_server, daemon=True).start()

    iface = meshtastic.serial_interface.SerialInterface(devPath=args.port)
    set_interface(iface)

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
        start_mqtt_client(iface.myInfo.my_node_num, **mqtt_config)

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
