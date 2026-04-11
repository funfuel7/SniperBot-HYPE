import os
import time
import requests

API_URL = "https://api.hyperliquid.xyz"

# ==============================
# CONFIG
# ==============================

SYMBOL = "BTC"
SIZE = 0.001  # test size

# ==============================
# GET PRICE
# ==============================

def get_price():
    try:
        res = requests.post(f"{API_URL}/info", json={"type": "allMids"})
        data = res.json()
        return float(data[SYMBOL])
    except Exception as e:
        print("PRICE ERROR:", e)
        return None

# ==============================
# CORRECT ORDER REQUEST
# ==============================

def send_order():
    price = get_price()

    if not price:
        print("No price")
        return

    print("\n🚀 TEST ORDER START")
    print("Price:", price)

    # ⚠️ Correct format for Hyperliquid test
    payload = {
        "type": "order",
        "orders": [
            {
                "coin": SYMBOL,
                "isBuy": True,
                "sz": SIZE,
                "limitPx": price,
                "orderType": {"limit": {"tif": "Ioc"}}
            }
        ]
    }

    try:
        res = requests.post(f"{API_URL}/exchange", json=payload)

        print("\n📥 RESPONSE:")
        print(res.text)

    except Exception as e:
        print("ORDER ERROR:", e)

# ==============================
# MAIN
# ==============================

def run():
    print("🚀 BOT STARTED")

    send_order()

    while True:
        time.sleep(30)


if __name__ == "__main__":
    run()
