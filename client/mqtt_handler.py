import json
import logging
import paho.mqtt.client as mqtt
from db_utils import save_command, save_position
from meshtastic_utils import set_node_position

mqtt_client = None

def on_mqtt_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        cmd = payload.get("cmd")
        logging.info(f"MQTT cmd ricevuto: {cmd} -> {payload}")
        save_command(cmd, payload)

        if cmd == "update":
            import subprocess
            subprocess.run(["./berry-update.sh"], check=False)

        elif cmd == "reboot":
            import subprocess
            subprocess.run(["reboot"], check=False)

        elif cmd == "set-position":
            lat = payload.get("lat")
            lng = payload.get("lng")
            if lat is not None and lng is not None:
                save_position(lat, lng, source="mqtt")
                set_node_position(lat, lng)

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
    mqtt_client.subscribe(f"{topic_base}/{node_id}/commands")
    logging.info(f"MQTT sottoscritto a: {topic_base}/{node_id}/commands")

def publish_packet_mqtt(packet, node_id, topic_base):
    if mqtt_client:
        mqtt_client.publish(f"{topic_base}/{node_id}/packets", json.dumps(packet))
