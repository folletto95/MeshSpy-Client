from flask import Flask, jsonify, request
from db_utils import save_command, save_position
from meshtastic_utils import set_node_position
import sqlite3

app = Flask(__name__)

@app.route("/status", methods=["GET"])
def status():
    with sqlite3.connect("packets.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM node_info LIMIT 1")
        node = c.fetchone()
        c.execute("SELECT lat, lng, timestamp FROM position ORDER BY timestamp DESC LIMIT 1")
        pos = c.fetchone()
    return jsonify({
        "node": {
            "id": node[1], "name": node[2], "short": node[3],
            "hw": node[4], "fw": node[5], "updated": node[6]
        } if node else None,
        "last_position": {
            "lat": pos[0], "lng": pos[1], "timestamp": pos[2]
        } if pos else None
    })

@app.route("/set-position", methods=["POST"])
def set_position():
    data = request.json
    lat = data.get("lat")
    lng = data.get("lng")
    if lat is not None and lng is not None:
        save_position(lat, lng, source="rest")
        save_command("set-position", data)
        set_node_position(lat, lng)
        return jsonify({"status": "ok"})
    return jsonify({"error": "lat/lng richiesti"}), 400

@app.route("/logs", methods=["GET"])
def logs():
    with sqlite3.connect("packets.db") as conn:
        c = conn.cursor()
        c.execute("SELECT cmd, payload, timestamp FROM commands ORDER BY timestamp DESC LIMIT 50")
        rows = c.fetchall()
    return jsonify([
        {"cmd": r[0], "payload": r[1], "timestamp": r[2]} for r in rows
    ])
