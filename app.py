from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

def calculate_signal(pair):
    data = yf.download(pair, interval="1m", period="1d")

    data['EMA'] = data['Close'].ewm(span=20).mean()

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    last = data.iloc[-1]

    if last['RSI'] < 30 and last['Close'] > last['EMA']:
        return "UP", "RSI Oversold + EMA Support"
    elif last['RSI'] > 70 and last['Close'] < last['EMA']:
        return "DOWN", "RSI Overbought + EMA Resistance"
    else:
        return "NO TRADE", "Market Neutral"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signal", methods=["POST"])
def signal():
    pair = request.json['pair']

    mapping = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X",
        "AUDUSD": "AUDUSD=X"
    }

    symbol = mapping.get(pair, "EURUSD=X")

    direction, reason = calculate_signal(symbol)

    return jsonify({
        "pair": pair,
        "direction": direction,
        "reason": reason
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))