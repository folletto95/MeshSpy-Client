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

def save_packet_to_db(packet):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                packet_json TEXT
            )
        ''')
        c.execute('INSERT INTO packets (packet_json) VALUES (?)', (json.dumps(packet),))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Errore nel salvataggio pacchetto: {e}")


def save_command(command):
    print(f"[DEBUG] Comando ricevuto da MQTT: {command}")
    # Da implementare logica di salvataggio comando, se necessaria

def save_position(position):
    print(f"[DEBUG] Posizione ricevuta da MQTT: {position}")
    # Da implementare logica di salvataggio posizione, se necessaria

def get_all_packets():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT packet_json FROM packets")
        rows = c.fetchall()
        conn.close()
        return [json.loads(row[0]) for row in rows]
    except Exception as e:
        print(f"[ERROR] Errore nel recupero pacchetti: {e}")
        return []
    
def get_node_info():
    # Placeholder: ritorna un esempio statico
    return [{"nodeId": "dummy", "info": "placeholder"}]

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def update_node_position(node_id, position):
    print(f"[DEBUG] Aggiorna posizione per {node_id}: {position}")
    # Da implementare logica reale se necessario