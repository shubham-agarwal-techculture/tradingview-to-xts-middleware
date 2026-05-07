# TradingView to XTS Broker Middleware

A robust, real-time middleware designed to bridge TradingView alerts with the XTS Broker API. This system captures webhooks, executes orders, and provides a premium dashboard for monitoring open and closed positions.

## 🚀 Features

- **Webhook Integration**: Securely receives JSON alerts from TradingView.
- **Order Execution**: Automatically forwards orders to the XTS Broker (simulated via Dummy API).
- **Premium Dashboard**: A sleek, dark-mode interface with real-time updates.
- **Position Management**: 
    - Track **Open Positions** with entry price and time.
    - Track **Closed Positions** with exit price and time.
    - **Manual Square-Off**: One-click position closing directly from the UI.
- **Persistent Memory**: All history (alerts, orders, positions) is saved to local JSON databases, surviving server restarts.
- **Simulated Environment**: Includes a `dummy_xts_api.py` for risk-free testing.

---

## 🛠️ Project Structure

```text
├── app.py                # Main Webhook Receiver & Dashboard Server
├── dummy_xts_api.py      # Simulated XTS Broker API
├── templates/
│   └── index.html        # Premium Dashboard Frontend
├── db_app.json           # Persistent store for alerts/orders
├── db_broker.json        # Persistent store for broker positions
└── requirements.txt      # Python dependencies
```

---

## ⚡ Setup Instructions

### 1. Environment Setup
Clone the repository and create a virtual environment:
```bash
python -m venv .venv
source .venv/Scripts/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Dummy Broker (Simulated XTS)
In a dedicated terminal, start the broker API:
```bash
python dummy_xts_api.py
```
*Runs on: http://127.0.0.1:8000*

### 3. Run the Middleware App
In another terminal, start the main application:
```bash
python app.py
```
*Runs on: http://127.0.0.1:5000*

### 4. Expose to Internet (ngrok)
To receive alerts from TradingView, expose your local port 5000:
```bash
ngrok http 5000
```
Copy the **Forwarding URL** provided by ngrok (e.g., `https://xyz.ngrok-free.app`).

---

## 📈 TradingView Configuration

1. Create a new Alert on TradingView.
2. Set the **Webhook URL** to: `https://your-ngrok-url/webhook`
3. Set the **Message** (JSON format) as follows:
```json
{
    "symbol": "NIFTY50",
    "action": "BUY",
    "price": "{{close}}"
}
```

---

## 🖥️ Dashboard Overview

- **TradingView Alerts**: Live feed of incoming webhooks.
- **Order History**: Logs of successful or failed order placements.
- **Open Positions**: Active trades with a manual "Square Off" button.
- **Closed Positions**: Historical view of completed trades with timestamps.

---

## 🛠️ Troubleshooting

- **No Logs?**: Ensure both `app.py` and `dummy_xts_api.py` are running and that `ngrok` is pointing to port 5000.
- **Connection Errors**: Check if the `requests` library is installed correctly.
- **Data Reset**: Delete `db_app.json` and `db_broker.json` to clear all history.

---

## 📜 License
MIT License - Created for automated trading research and execution.
