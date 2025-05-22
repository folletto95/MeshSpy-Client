import sqlite3
import logging
from datetime import datetime

DB_PATH = "mesh_packets.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sender TEXT,
            type TEXT,
            payload TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_packet(packet):
    logging.debug(f"Salvataggio del pacchetto: {packet}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO packets (timestamp, sender, type, payload)
        VALUES (?, ?, ?, ?)
    ''', (
        datetime.utcnow().isoformat(),
        packet.get("from", "unknown"),
        packet.get("decoded", {}).get("portnum", "unknown"),
        str(packet)
    ))
    conn.commit()
    conn.close()

def save_command(packet):
    logging.debug(f"Salvataggio del comando: {packet}")
    save_packet(packet)

def save_position(packet):
    logging.debug(f"Salvataggio della posizione: {packet}")
    save_packet(packet)

def get_all_packets():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM packets ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def update_node_info(node_id, info):
    # Implementa la logica per aggiornare le informazioni del nodo
    pass
