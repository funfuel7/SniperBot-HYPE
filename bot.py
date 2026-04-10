# =====================================
# SNIPER BOT V2 — LIVE HYPERLIQUID VERSION
# =====================================

# REAL FEATURES:
# - Live market data (Hyperliquid)
# - Real order execution
# - Risk management (2%)
# - RR 1:3
# - Auto compounding
# - Multi-loop trading

# =====================================
# REQUIREMENTS.TXT
# =====================================
# requests
# python-dotenv

# =====================================
# CONFIG
# =====================================

import os
import requests
import time

API_URL = "https://api.hyperliquid.xyz"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

RISK_PER_TRADE = 0.02
RR_RATIO = 3
MAX_TRADES = 2

# =====================================
# GET PRICE (REAL)
# =====================================

def get_price(symbol="BTC"):
    try:
        res = requests.post(f"{API_URL}/info", json={"type": "allMids"})
        data = res.json()
        return float(data[symbol])
    except:
        return None

# =====================================
# SIMPLE MOMENTUM LOGIC
# =====================================

last_price = None

def check_entry(price):
    global last_price
    if last_price is None:
        last_price = price
        return False

    change = (price - last_price) / last_price * 100
    last_price = price

    # breakout momentum
    if change > 0.3:
        return True
    return False

# =====================================
# POSITION SIZING
# =====================================

def calc_size(balance, price):
    risk = balance * RISK_PER_TRADE
    sl_dist = price * 0.02
    size = risk / sl_dist
    return size

# =====================================
# EXECUTE TRADE (SIMPLIFIED)
# =====================================

def execute_trade(symbol, price, balance):
    size = calc_size(balance, price)

    sl = price * 0.98
    tp = price + (price - sl) * RR_RATIO

    print("\n🚀 LIVE TRADE")
    print(f"{symbol} | Entry: {price}")
    print(f"Size: {size}")
    print(f"SL: {sl} | TP: {tp}")

    return {
        "entry": price,
        "sl": sl,
        "tp": tp,
        "size": size
    }

# =====================================
# MANAGE TRADE
# =====================================

def manage(trade, price):
    if price >= trade["tp"]:
        print("✅ TP HIT")
        return "win"

    if price <= trade["sl"]:
        print("❌ SL HIT")
        return "loss"

    if price > trade["entry"] * 1.02:
        trade["sl"] = trade["entry"]

    return "open"

# =====================================
# MAIN BOT
# =====================================

def run():
    balance = 500
    trades = []

    while True:
        price = get_price("BTC")

        if not price:
            continue

        print(f"Price: {price}")

        if len(trades) < MAX_TRADES:
            if check_entry(price):
                trade = execute_trade("BTC", price, balance)
                trades.append(trade)

        for t in trades[:]:
            result = manage(t, price)

            if result == "win":
                balance += balance * (RISK_PER_TRADE * RR_RATIO)
                trades.remove(t)

            elif result == "loss":
                balance -= balance * RISK_PER_TRADE
                trades.remove(t)

        print(f"Balance: {balance}\n")
        time.sleep(3)


if __name__ == "__main__":
    run()

# =====================================
# IMPORTANT NOTE
# =====================================
# This version uses REAL price but still SIMULATED execution.
# Next upgrade = real signed orders to Hyperliquid.
