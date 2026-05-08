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
        pos_response = requests.get("http://localhost:8001/portfolio/positions")
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
        # Added timeout to prevent blocking the dashboard
        pos_response = requests.get("http://localhost:8001/portfolio/positions", timeout=1.5)
        pos_data = pos_response.json().get("data", {})
        open_positions = pos_data.get("positionList", [])
        closed_positions = pos_data.get("closedPositions", [])
    except Exception as e:
        print(f"Error fetching positions: {e}")
        open_positions = []
        closed_positions = []

    response = jsonify({
        "alerts": alerts,
        "orders": orders,
        "open_positions": open_positions,
        "closed_positions": closed_positions
    })
    # Prevent browser caching of logs
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # Allow Cross-Origin requests (e.g., from VS Code Live Server on Port 5500)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.route('/square_off', methods=['POST', 'OPTIONS'])
def square_off():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    data = request.json
    symbol = data.get("symbol")
    
    try:
        response_raw = requests.post(
            "http://localhost:8001/interactive/positions/squareoff",
            json={"symbol": symbol},
            timeout=2
        )
        resp_data = response_raw.json()
        response = jsonify(resp_data)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, response_raw.status_code
    except Exception as e:
        response = jsonify({"type": "error", "message": str(e)})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response, 500


@app.route('/webhook', methods=['POST'])
def webhook():
    # Use force=True to handle cases where Content-Type might not be application/json
    data = request.get_json(force=True)
    if not data:
        return {"status": "error", "message": "No JSON data received"}, 400

    symbol = data.get("symbol", "UNKNOWN")
    action = data.get("action", "UNKNOWN").upper()
    price = data.get("price", "0")

    alert = {
        "time": str(datetime.now()),
        "symbol": symbol,
        "action": action,
        "price": price
    }

    alerts.insert(0, alert)
    save_db({"alerts": alerts, "orders": orders})

    print(f"\nALERT RECEIVED: {symbol} {action} @ {price}", flush=True)

    # ---------------------------------
    # HIT DUMMY BROKER API
    # ---------------------------------
    try:
        broker_response = requests.post(
            "http://localhost:8001/interactive/orders",
            json={
                "symbol": symbol,
                "action": action,
                "price": price
            },
            timeout=2
        )
        status_msg = broker_response.json().get("message", "Order placed")
    except Exception as e:
        status_msg = f"Broker Error: {str(e)}"

    order = {
        "time": str(datetime.now()),
        "symbol": symbol,
        "action": action,
        "status": status_msg
    }

    orders.insert(0, order)
    save_db({"alerts": alerts, "orders": orders})

    print(f"ORDER STATUS: {status_msg}", flush=True)

    return {"status": "success"}, 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)