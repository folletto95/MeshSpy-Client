import sqlite3
import os
from threading import Lock

_DB_PATH = "backend/data/nodes.db"
_lock = Lock()

def init_db():
    """Crea le tabelle nodes e nodes_history se non esistono."""
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    with _lock, sqlite3.connect(_DB_PATH) as conn:
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

def register_node(node_id: str, name: str):
    """
    Registra un nuovo nodo:
    - Se non esiste, inserisce id, name e first_seen
    - Se esiste, non fa nulla
    """
    init_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute("""
            INSERT INTO nodes (id, name)
            VALUES (?, ?)
            ON CONFLICT(id) DO NOTHING
        """, (node_id, name))
        conn.commit()

def get_display_name(id: str) -> str:
    """
    Restituisce longname se presente, altrimenti shortname,
    altrimenti l'id stesso.
    """
    init_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        cur = conn.execute(
            "SELECT longname, shortname FROM nodes WHERE id = ?", (id,)
        )
        row = cur.fetchone()
        if row:
            longn, short = row
            if longn:
                return longn
            if short:
                return short
    return id

def upsert_nodeinfo(id: str, short: str, long: str, name: str):
    """
    Aggiorna o inserisce i campi shortname/longname e registra l'evento.
    """
    init_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        # 1) Assicura esistenza nodo
        conn.execute("""
            INSERT INTO nodes (id, name)
            VALUES (?, ?)
            ON CONFLICT(id) DO NOTHING
        """, (id, name))

        # 2) Recupera dati attuali
        cur = conn.execute("SELECT shortname, longname FROM nodes WHERE id = ?", (id,))
        current = cur.fetchone() or ("", "")
        current_short, current_long = current

        new_short = short if short else current_short
        new_long = long if long else current_long

        if new_short != current_short or new_long != current_long:
            conn.execute("""
                UPDATE nodes
                SET shortname = ?, longname = ?
                WHERE id = ?
            """, (new_short, new_long, id))

        # 3) Storico dell’evento nodeinfo
        conn.execute("""
            INSERT INTO nodes_history (id, event_type, data)
            VALUES (?, 'nodeinfo', ?)
        """, (id, f'{{"short": "{short}", "long": "{long}"}}'))
        conn.commit()

def update_position(id: str, x: float, y: float):
    """
    Aggiorna last_x, last_y e last_seen solo se la posizione è cambiata.
    """
    init_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
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

    return {"status": "ok", "id": id, "x": x, "y": y}

def store_event(id: str, event_type: str, data: str):
    """
    Storicizza ogni messaggio nella tabella nodes_history.
    """
    init_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute("""
            INSERT INTO nodes_history (id, event_type, data)
            VALUES (?, ?, ?)
        """, (id, event_type, data))
        conn.commit()