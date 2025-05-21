import sqlite3
import json
import logging

DB_FILE = "packets.db"

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
        c.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cmd TEXT,
                payload TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS position (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lat REAL,
                lng REAL,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS node_info (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                node_num TEXT,
                long_name TEXT,
                short_name TEXT,
                hw_model TEXT,
                firmware_version TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_packet(packet):
    try:
        logging.info(f"[SAVE] Analizzo pacchetto: {packet}")

        decoded = packet.get("decoded", {})
        message = decoded.get("payload")
        packet_type = decoded.get("portnum")
        from_node = packet.get("from", "UNKNOWN")
        to_node = packet.get("to", "UNKNOWN")
        raw_json = json.dumps(packet)

        if message is None:
            logging.warning("[SAVE] Pacchetto scartato: manca 'payload'")
            return
        if packet_type is None:
            logging.warning("[SAVE] Pacchetto scartato: manca 'portnum'")
            return

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO packets (from_node, to_node, message, packet_type, raw_json)
                VALUES (?, ?, ?, ?, ?)
            """, (from_node, to_node, message, packet_type, raw_json))
            conn.commit()
            logging.info("[SAVE] Pacchetto salvato nel DB")

    except Exception as e:
        logging.error(f"[SAVE] Errore nel salvataggio pacchetto: {e}")


def save_command(cmd, payload):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO commands (cmd, payload) VALUES (?, ?)", (cmd, json.dumps(payload)))
        conn.commit()

def save_position(lat, lng, source="manual"):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO position (lat, lng, source) VALUES (?, ?, ?)", (lat, lng, source))
        conn.commit()

def update_node_info(node_num, long_name, short_name, hw_model, firmware_version):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO node_info (id, node_num, long_name, short_name, hw_model, firmware_version)
            VALUES (1, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                node_num=excluded.node_num,
                long_name=excluded.long_name,
                short_name=excluded.short_name,
                hw_model=excluded.hw_model,
                firmware_version=excluded.firmware_version,
                last_updated=CURRENT_TIMESTAMP
        """, (node_num, long_name, short_name, hw_model, firmware_version))
        conn.commit()
