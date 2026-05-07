from flask import Flask, request, render_template, jsonify
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

DB_FILE = 'db_app.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"alerts": [], "orders": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_db()
alerts = db["alerts"]
orders = db["orders"]


@app.route('/')
def dashboard():
    try:
        pos_response = requests.get("http://localhost:8000/portfolio/positions")
        pos_data = pos_response.json().get("data", {})
        open_positions = pos_data.get("positionList", [])
        closed_positions = pos_data.get("closedPositions", [])
    except Exception:
        open_positions = []
        closed_positions = []

    return render_template(
        'index.html',
        alerts=alerts,
        orders=orders,
        open_positions=open_positions,
        closed_positions=closed_positions
    )


@app.route('/logs')
def get_logs():
    try:
        pos_response = requests.get("http://localhost:8000/portfolio/positions")
        pos_data = pos_response.json().get("data", {})
        open_positions = pos_data.get("positionList", [])
        closed_positions = pos_data.get("closedPositions", [])
    except Exception:
        open_positions = []
        closed_positions = []

    return jsonify({
        "alerts": alerts,
        "orders": orders,
        "open_positions": open_positions,
        "closed_positions": closed_positions
    })


@app.route('/square_off', methods=['POST'])
def square_off():
    data = request.json
    symbol = data.get("symbol")
    
    try:
        response = requests.post(
            "http://localhost:8000/interactive/positions/squareoff",
            json={"symbol": symbol}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"type": "error", "message": str(e)}), 500


@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    alert = {
        "time": str(datetime.now()),
        "symbol": data.get("symbol"),
        "action": data.get("action"),
        "price": data.get("price")
    }

    alerts.insert(0, alert)
    save_db({"alerts": alerts, "orders": orders})

    print("\nALERT RECEIVED:", alert, flush=True)

    # ---------------------------------
    # HIT DUMMY BROKER API
    # ---------------------------------

    broker_response = requests.post(
        "http://localhost:8000/interactive/orders",
        json={
            "symbol": data.get("symbol"),
            "action": data.get("action"),
            "price": data.get("price")
        }
    )

    order = {
        "time": str(datetime.now()),
        "symbol": data.get("symbol"),
        "action": data.get("action"),
        "status": broker_response.json().get("message")
    }

    orders.insert(0, order)
    save_db({"alerts": alerts, "orders": orders})

    print("ORDER RESPONSE:", order, flush=True)

    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)