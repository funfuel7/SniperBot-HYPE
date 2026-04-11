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

SYMBOL = "BTC"

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
    except Exception as e:
        print("PRICE ERROR:", e)
        return None

# ==============================
# SEND ORDER (DEBUG MODE)
# ==============================

def send_order():
    price = get_price()

    if not price:
        print("No price, aborting")
        return

    size = 0.001  # VERY SMALL TEST SIZE

    print("\n⚠️ SENDING TEST ORDER")
    print(f"Price: {price}")
    print(f"Size: {size}")

    order = {
        "type": "order",
        "orders": [
            {
                "coin": SYMBOL,
                "isBuy": True,
                "sz": size,
                "limitPx": round(price, 2),
                "orderType": {"limit": {"tif": "Ioc"}}
            }
        ]
    }

    message = json.dumps(order)

    try:
        signed = account.sign_message(
            encode_defunct(text=message)
        )

        payload = {
            "action": order,
            "signature": signed.signature.hex(),
            "address": address
        }

        print("\n📤 PAYLOAD:")
        print(payload)

        res = requests.post(f"{API_URL}/exchange", json=payload)

        print("\n📥 RAW RESPONSE:")
        print(res.text)

    except Exception as e:
        print("❌ ORDER ERROR:", e)

# ==============================
# MAIN
# ==============================

def run():
    print("🚀 BOT STARTED")

    # FORCE ONE ORDER
    send_order()

    print("\n⏳ Waiting... (bot idle after test)")

    while True:
        time.sleep(30)


if __name__ == "__main__":
    run()
