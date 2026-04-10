import os
import time
import json
import requests
from eth_account import Account
from eth_account.messages import encode_defunct

# ==============================
# CONFIG
# ==============================

API_URL = "https://api.hyperliquid.xyz"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

RISK_PER_TRADE = 0.02
RR_RATIO = 3
MAX_TRADES = 1

SYMBOL = "BTC"

COOLDOWN = 20  # seconds between trades

# ==============================
# WALLET
# ==============================

account = Account.from_key(PRIVATE_KEY)
address = account.address

print("Using wallet:", address)

# ==============================
# GET PRICE
# ==============================

def get_price():
    try:
        res = requests.post(f"{API_URL}/info", json={"type": "allMids"})
        data = res.json()
        return float(data[SYMBOL])
    except:
        return None

# ==============================
# ENTRY LOGIC (VERY SENSITIVE)
# ==============================

last_price = None
last_trade_time = 0

def check_entry(price):
    global last_price, last_trade_time

    if last_price is None:
        last_price = price
        return False

    change = (price - last_price) / last_price * 100
    last_price = price

    print(f"Change: {round(change, 5)}%")

    # cooldown to prevent spam
    if time.time() - last_trade_time < COOLDOWN:
        return False

    # VERY sensitive for testing
    if change > 0.005:
        print("📈 Momentum detected (TEST MODE)")
        last_trade_time = time.time()
        return True

    return False

# ==============================
# POSITION SIZE
# ==============================

def calc_size(balance, price):
    risk = balance * RISK_PER_TRADE
    sl_distance = price * 0.02
    size = risk / sl_distance
    return round(size, 4)

# ==============================
# SEND ORDER
# ==============================

def send_order(is_buy, size, price):
    order = {
        "type": "order",
        "orders": [
            {
                "coin": SYMBOL,
                "isBuy": is_buy,
                "sz": size,
                "limitPx": round(price, 2),
                "orderType": {"limit": {"tif": "Ioc"}}
            }
        ]
    }

    message = json.dumps(order)

    signed = account.sign_message(
        encode_defunct(text=message)
    )

    payload = {
        "action": order,
        "signature": signed.signature.hex(),
        "address": address
    }

    try:
        res = requests.post(f"{API_URL}/exchange", json=payload)
        print("ORDER RESPONSE:", res.json())
    except Exception as e:
        print("ERROR:", e)

# ==============================
# EXECUTE TRADE
# ==============================

def execute_trade(balance, price):
    size = calc_size(balance, price)

    if size <= 0:
        return None

    sl = price * 0.98
    tp = price + (price - sl) * RR_RATIO

    print("\n🚀 TRADE OPENED")
    print(f"Entry: {price}")
    print(f"Size: {size}")
    print(f"SL: {sl}")
    print(f"TP: {tp}")

    send_order(True, size, price)

    return {
        "entry": price,
        "sl": sl,
        "tp": tp,
        "size": size
    }

# ==============================
# MANAGE TRADE
# ==============================

def manage_trade(trade, price, balance):
    if price >= trade["tp"]:
        print("✅ TP HIT")
        send_order(False, trade["size"], price)
        return "win"

    if price <= trade["sl"]:
        print("❌ SL HIT")
        send_order(False, trade["size"], price)
        return "loss"

    if price > trade["entry"] * 1.02:
        trade["sl"] = trade["entry"]

    return "open"

# ==============================
# MAIN LOOP
# ==============================

def run():
    balance = 150
    trades = []

    while True:
        price = get_price()

        if not price:
            continue

        print(f"Price: {price}")

        # ENTRY
        if len(trades) < MAX_TRADES:
            if check_entry(price):
                trade = execute_trade(balance, price)
                if trade:
                    trades.append(trade)

        # MANAGEMENT
        for t in trades[:]:
            result = manage_trade(t, price, balance)

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
