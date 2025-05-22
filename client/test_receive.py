import time
import logging
from pubsub import pub
import meshtastic.serial_interface

logging.basicConfig(level=logging.DEBUG)

def on_receive(packet, interface):
    print("=== Ricevuto pacchetto ===")
    print(packet)

def on_connection(interface, topic=pub.AUTO_TOPIC):
    print("=== Connesso ===")

pub.subscribe(on_receive, "meshtastic.receive")
pub.subscribe(on_connection, "meshtastic.connection.established")

print("Inizio connessione al nodo Meshtastic...")

iface = meshtastic.serial_interface.SerialInterface(devPath="/dev/ttyACM0")

print("Loop in attesa di pacchetti...")
while True:
    time.sleep(1)
