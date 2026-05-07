#####################################
# DUMMY XTS API
#####################################

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DB_FILE = 'db_broker.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            # Handle migration from old format if needed
            if isinstance(data, dict) and "open" in data:
                return data
            return {"open": data, "closed": []}
    return {"open": {}, "closed": []}

def save_db(open_pos, closed_pos):
    with open(DB_FILE, 'w') as f:
        json.dump({"open": open_pos, "closed": closed_pos}, f, indent=4)

db_data = load_db()
open_positions = db_data["open"]
closed_positions = db_data["closed"]

@app.route('/interactive/orders', methods=['POST'])
def place_order():
    data = request.json
    symbol = data.get("symbol")
    side = data.get("action")
    price = data.get("price")
    
    print(f"\n===== DUMMY XTS ORDER RECEIVED: {side} {symbol} =====", flush=True)
    
    # Update dummy positions
    open_positions[symbol] = {
        "symbol": symbol, 
        "side": side, 
        "price": price, 
        "open_time": str(datetime.now())
    }
    save_db(open_positions, closed_positions)

    return {
        "type": "success",
        "message": "Order placed successfully",
        "order_id": "DUMMY123"
    }, 200

@app.route('/portfolio/positions', methods=['GET'])
def get_positions():
    return jsonify({
        "data": {
            "positionList": list(open_positions.values()),
            "closedPositions": closed_positions
        }
    }), 200

@app.route('/interactive/positions/squareoff', methods=['POST'])
def square_off():
    data = request.json
    symbol = data.get("symbol")
    
    if symbol in open_positions:
        pos = open_positions.pop(symbol)
        pos["close_time"] = str(datetime.now())
        pos["close_price"] = data.get("price", "Market") # Use provided price or default
        closed_positions.insert(0, pos)
        
        save_db(open_positions, closed_positions)
        print(f"===== DUMMY XTS POSITION SQUARED OFF: {symbol} =====", flush=True)
        return {"type": "success", "message": f"Squared off {symbol}"}, 200
    else:
        return {"type": "error", "message": "Position not found"}, 404


if __name__ == '__main__':
    app.run(port=8000, debug=True)