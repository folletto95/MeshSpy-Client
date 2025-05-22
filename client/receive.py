from pubsub import pub
from meshtastic_utils import print_node_info
from db_utils import save_packet_to_db as save_packet

def on_receive(packet, interface):
    """Handler per la ricezione dei pacchetti."""
    print("\n=== Ricevuto pacchetto ===")
    print(packet)
    save_packet(packet)

def on_connection(interface, topic=pub.AUTO_TOPIC):
    """Handler per la connessione al nodo."""
    print("[INFO] Connesso al nodo Meshtastic")
    print_node_info(interface)
