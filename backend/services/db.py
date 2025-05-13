import sqlite3
from typing import Optional, Dict

DB_PATH = "/mnt/data/nodes.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            name TEXT,
            last_x REAL,
            last_y REAL,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def register_node(node_id: str, name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO nodes (id, name) VALUES (?, ?)
    ''', (node_id, name))
    conn.commit()
    conn.close()

def upsert_nodeinfo(node_id: str, shortname: str, longname: str, name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO nodes (id, name) VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET name=excluded.name
    ''', (node_id, name))
    conn.commit()
    conn.close()

def update_position(node_id: str, lat: float, lon: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE nodes SET last_x = ?, last_y = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?
    ''', (lat, lon, node_id))
    conn.commit()
    conn.close()

def get_position(node_id: str) -> Optional[Dict[str, float]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT last_x, last_y FROM nodes WHERE id = ?
    ''', (node_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"lat": row[0], "lon": row[1]}
    return None
