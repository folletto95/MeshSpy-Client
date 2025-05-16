import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel

DB_FOLDER = os.getenv("MESHSERVER_DB_PATH", str(Path.home() / ".meshspy_data"))
DB_FILENAME = "node.db"
DB_PATH = os.path.join(DB_FOLDER, DB_FILENAME)

os.makedirs(DB_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_path():
    return DB_PATH

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            node_id INTEGER UNIQUE NOT NULL,
            name TEXT,
            last_seen TEXT,
            latitude REAL,
            longitude REAL,
            altitude REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            node_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()

def insert_node(node_id: int, name: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO nodes (node_id, name, last_seen)
        VALUES (?, ?, ?)
        """,
        (node_id, name, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def update_nodeinfo(node_id: int, name: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE nodes
        SET name = ?, last_seen = ?
        WHERE node_id = ?
        """,
        (name, datetime.utcnow().isoformat(), node_id)
    )
    conn.commit()
    conn.close()

def update_position(node_id: int, latitude: float, longitude: float, altitude: Optional[float] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE nodes
        SET latitude = ?, longitude = ?, altitude = ?, last_seen = ?
        WHERE node_id = ?
        """,
        (latitude, longitude, altitude, datetime.utcnow().isoformat(), node_id)
    )
    conn.commit()
    conn.close()

def load_nodes_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nodes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def store_event(node_id: str, topic: str, payload: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO events (timestamp, node_id, topic, payload)
        VALUES (?, ?, ?, ?)
        """,
        (datetime.utcnow().isoformat(), node_id, topic, payload)
    )
    conn.commit()
    conn.close()

class Node(BaseModel):
    node_id: int
    name: Optional[str] = None
