import sqlite3
import os
import logging
from threading import Lock

logging.basicConfig(level=logging.DEBUG)

DB_DIR = os.path.expanduser("~/.meshspy_data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "node.db")
_lock = Lock()

def init_db():
    """Crea le tabelle nodes e nodes_history se non esistono."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            first_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            shortname TEXT,
            longname TEXT,
            last_x REAL,
            last_y REAL,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes_history (
            hist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT,
            ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        logging.debug("DB inizializzato")

def register_node(node_id: str, name: str):
    init_db()
    with _lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO nodes (id, name)
            VALUES (?, ?)
            ON CONFLICT(id) DO NOTHING
        """, (node_id, name))
        conn.commit()
        logging.debug(f"Registrato nodo: {node_id} - {name}")

def get_display_name(id: str) -> str:
    init_db()
    with _lock, sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT longname, shortname FROM nodes WHERE id = ?", (id,)
        )
        row = cur.fetchone()
        if row:
            longn, short = row
            return longn or short or id
    return id

def upsert_nodeinfo(id: str, short: str, long: str, name: str):
    init_db()
    with _lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO nodes (id, name)
            VALUES (?, ?)
            ON CONFLICT(id) DO NOTHING
        """, (id, name))

        cur = conn.execute("SELECT shortname, longname FROM nodes WHERE id = ?", (id,))
        current = cur.fetchone() or ("", "")
        current_short, current_long = current

        new_short = short or current_short
        new_long = long or current_long

        if new_short != current_short or new_long != current_long:
            conn.execute("""
                UPDATE nodes
                SET shortname = ?, longname = ?
                WHERE id = ?
            """, (new_short, new_long, id))

        conn.execute("""
            INSERT INTO nodes_history (id, event_type, data)
            VALUES (?, 'nodeinfo', ?)
        """, (id, f'{{"short": "{short}", "long": "{long}"}}'))
        conn.commit()
        logging.debug(f"Aggiornato nodo: {id}")

def update_position(id: str, x: float, y: float):
    init_db()
    with _lock, sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT last_x, last_y FROM nodes WHERE id = ?", (id,)
        )
        row = cur.fetchone()

        if not row or row[0] != x or row[1] != y:
            conn.execute("""
                UPDATE nodes
                SET last_x = ?, last_y = ?, last_seen = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (x, y, id))
            conn.execute("""
                INSERT INTO nodes_history (id, event_type, data)
                VALUES (?, 'position', ?)
            """, (id, f'{{"x": {x}, "y": {y}}}'))
            conn.commit()
            logging.debug(f"Posizione aggiornata per {id}: x={x}, y={y}")

    return {"status": "ok", "id": id, "x": x, "y": y}

def store_event(id: str, event_type: str, data: str):
    init_db()
    with _lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO nodes_history (id, event_type, data)
            VALUES (?, ?, ?)
        """, (id, event_type, data))
        conn.commit()
        logging.debug(f"Evento salvato: {event_type} per {id}")
