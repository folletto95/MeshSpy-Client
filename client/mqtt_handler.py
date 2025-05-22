import time
import paho.mqtt.client as mqtt

# from db_utils import save_command, save_position  # Commentato perché non esistono

def start_mqtt_client(node_num, host, port, username=None, password=None, topic_prefix="msh/EU_868"):
    topic = f"{topic_prefix}/{node_num}/commands"

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"[INFO] MQTT sottoscritto a: {topic}")
            client.subscribe(topic)
        else:
            print(f"[ERROR] MQTT connection failed with code {rc}")

    def on_message(client, userdata, msg):
        print(f"[DEBUG] Ricevuto comando MQTT: {msg.payload.decode()}")
        # save_command(msg.payload.decode())  # Stub: da implementare se serve

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    if username and password:
        client.username_pw_set(username, password)

    client.connect(host, port, 60)

    client.loop_start()
    return client
