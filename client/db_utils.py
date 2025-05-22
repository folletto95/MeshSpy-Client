import sqlite3
import time

DB_FILE = "packets.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS packets (
                id TEXT PRIMARY KEY,
                from_node TEXT,
                to_node TEXT,
                message TEXT,
                packet_type TEXT,
                timestamp INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS node_info (
                node_num INTEGER PRIMARY KEY,
                long_name TEXT,
                short_name TEXT,
                hw_model TEXT,
                firmware_version TEXT,
                last_seen INTEGER
            )
        """)
        conn.commit()

def save_packet(packet):
    from_node = packet.get("fromId")
    to_node = packet.get("toId")
    message = packet.get("decoded", {}).get("text") or packet.get("decoded", {}).get("position")
    packet_type = packet.get("decoded", {}).get("portnum")
    timestamp = packet.get("rxTime", int(time.time()))
    packet_id = str(packet.get("id"))

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO packets VALUES (?, ?, ?, ?, ?, ?)", 
                  (packet_id, from_node, to_node, str(message), packet_type, timestamp))
        conn.commit()

def update_node_info(node_num, long_name, short_name, hw_model, firmware_version):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO node_info 
            (node_num, long_name, short_name, hw_model, firmware_version, last_seen) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (node_num, long_name, short_name, hw_model, firmware_version, int(time.time())))
        conn.commit()
