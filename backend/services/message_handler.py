from backend.services.db import get_db_connection
from datetime import datetime

def insert_or_update_node_from_message(message: dict):
    node_id = message.get("from")
    if node_id is None:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    # Inserimento se non esiste
    cursor.execute(
        "INSERT OR IGNORE INTO nodes (node_id, name, last_seen) VALUES (?, ?, ?)",
        (node_id, str(node_id), datetime.utcnow().isoformat())
    )

    # Aggiornamento dati noti
    lat = lon = alt = None
    name = None
    update_position = False

    msg_type = message.get("type")
    if msg_type == "position":
        lat = message.get("lat")
        lon = message.get("lon")
        alt = message.get("altitude")
        if lat not in (None, 0) and lon not in (None, 0):
            update_position = True
    elif msg_type == "nodeinfo":
        payload = message.get("payload", {})
        name = payload.get("longname") or payload.get("shortname")

    updates = []
    params = []

    if name:
        updates.append("name = ?")
        params.append(name)
    if update_position:
        updates.extend(["latitude = ?", "longitude = ?"])
        params.extend([lat, lon])
        if alt is not None:
            updates.append("altitude = ?")
            params.append(alt)

    updates.append("last_seen = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(node_id)

    if updates:
        sql = f"UPDATE nodes SET {', '.join(updates)} WHERE node_id = ?"
        cursor.execute(sql, params)

    conn.commit()
    conn.close()