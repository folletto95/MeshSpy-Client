import logging
from db_utils import save_packet

def on_receive(packet):
    logging.info(f"Pacchetto ricevuto: {packet}")
    save_packet(packet)

def on_connection(interface):
    logging.info("Connessione stabilita con l'interfaccia Meshtastic.")
