from flask import Flask, jsonify, render_template, request
from db_utils import get_all_packets, get_node_info, update_node_position

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/packets")
def packets():
    packets = get_all_packets()
    return jsonify(packets)

@app.route("/status")
def status():
    return jsonify({"status": "running"})

@app.route("/logs")
def logs():
    # Placeholder: implementare log reading se necessario
    return jsonify({"logs": "Log output not implemented yet."})

@app.route("/set-position", methods=["POST"])
def set_position():
    data = request.json
    try:
        node_num = data["node_num"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        altitude = data.get("altitude", 0)
        update_node_position(node_num, latitude, longitude, altitude)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/node/<int:node_num>")
def node_info(node_num):
    info = get_node_info(node_num)
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "Node not found"}), 404

def start_flask_server():
    app.run(host="0.0.0.0", port=5000)
