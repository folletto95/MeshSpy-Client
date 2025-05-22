import sqlite3
import time
import logging

DB_FILE = "packets.db"
logging.basicConfig(level=logging.DEBUG)


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_id TEXT,
                to_id TEXT,
                portnum TEXT,
                payload TEXT,
                rx_time INTEGER,
                raw TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS node_info (
                node_num INTEGER PRIMARY KEY,
                long_name TEXT,
                short_name TEXT,
                hw_model TEXT,
                last_seen INTEGER,
                lat REAL,
                lon REAL,
                alt INTEGER
            )
        ''')
        conn.commit()


def save_packet_to_db(packet):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO packets (from_id, to_id, portnum, payload, rx_time, raw)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            packet.get('fromId'),
            packet.get('toId'),
            packet.get('decoded', {}).get('portnum'),
            str(packet.get('decoded', {}).get('payload')),
            int(packet.get('rxTime', time.time())),
            str(packet)
        ))
        conn.commit()


def get_all_packets():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM packets ORDER BY rx_time DESC")
        columns = [desc[0] for desc in c.description]
        return [dict(zip(columns, row)) for row in c.fetchall()]


def get_node_info():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM node_info")
        columns = [desc[0] for desc in c.description]
        return [dict(zip(columns, row)) for row in c.fetchall()]


def update_node_info(node_num, long_name=None, short_name=None, hw_model=None):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO node_info (node_num, long_name, short_name, hw_model, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(node_num) DO UPDATE SET
                long_name=excluded.long_name,
                short_name=excluded.short_name,
                hw_model=excluded.hw_model,
                last_seen=excluded.last_seen
        """, (node_num, long_name, short_name, hw_model, int(time.time())))
        conn.commit()


def update_node_position(node_num, lat, lon, alt):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE node_info
            SET lat = ?, lon = ?, alt = ?, last_seen = ?
            WHERE node_num = ?
        """, (lat, lon, alt, int(time.time()), node_num))
        conn.commit()
