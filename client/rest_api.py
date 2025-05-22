from flask import Flask, jsonify
import sqlite3

DB_FILE = "packets.db"
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "<h1>MeshSpy Client è attivo</h1><p>Usa <a href='/packets'>/packets</a> per i dati.</p>"

@app.route("/packets", methods=["GET"])
def get_all_packets():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, from_node, to_node, message, packet_type, timestamp FROM packets ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
        print(f"[DEBUG] Trovati {len(rows)} pacchetti nel DB.")
        for r in rows:
            print(f"[DEBUG] Pacchetto: {r}")
    return jsonify([
        {"id": r[0], "from": r[1], "to": r[2], "message": r[3], "type": r[4], "timestamp": r[5]} for r in rows
    ])

@app.route("/packets/grouped", methods=["GET"])
def get_packets_grouped():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT from_node, COUNT(*), MAX(timestamp) 
            FROM packets GROUP BY from_node ORDER BY MAX(timestamp) DESC
        """)
        rows = c.fetchall()
    return jsonify([
        {"from": r[0], "count": r[1], "last_seen": r[2]} for r in rows
    ])

def start_web_server():
    app.run(host="0.0.0.0", port=5000)
