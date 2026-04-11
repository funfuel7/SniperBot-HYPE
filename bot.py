import os
import time
import requests
import json
from eth_account import Account
from eth_account.messages import encode_defunct

API_URL = "https://api.hyperliquid.xyz"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

SYMBOL = "BTC"
SIZE = 0.001

# ==============================
# WALLET
# ==============================

account = Account.from_key(PRIVATE_KEY)
address = account.address

print("Using wallet:", address)

# ==============================
# GET NONCE
# ==============================

def get_nonce():
    try:
        res = requests.post(f"{API_URL}/info", json={
            "type": "clearinghouseState",
            "user": address
        })
        data = res.json()
        return data["nonce"]
    except Exception as e:
        print("Nonce error:", e)
        return int(time.time() * 1000)

# ==============================
# GET PRICE
# ==============================

def get_price():
    try:
        res = requests.post(f"{API_URL}/info", json={"type": "allMids"})
        data = res.json()
        return float(data[SYMBOL])
    except Exception as e:
        print("Price error:", e)
        return None

# ==============================
# SIGN ACTION
# ==============================

def sign_action(action, nonce):
    message = {
        "action": action,
        "nonce": nonce
    }

    encoded = json.dumps(message, separators=(',', ':'))

    signed = account.sign_message(
        encode_defunct(text=encoded)
    )

    return signed.signature.hex()

# ==============================
# SEND ORDER (CORRECT FORMAT)
# ==============================

def send_order():
    price = get_price()
    nonce = get_nonce()

    if not price:
        print("No price")
        return

    print("\n🚀 SENDING REAL TEST ORDER")
    print("Price:", price)
    print("Nonce:", nonce)

    action = {
        "type": "order",
        "orders": [
            {
                "coin": SYMBOL,
                "isBuy": True,
                "sz": SIZE,
                "limitPx": round(price, 2),
                "orderType": {"limit": {"tif": "Ioc"}}
            }
        ]
    }

    signature = sign_action(action, nonce)

    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "address": address
    }

    print("\n📤 PAYLOAD:")
    print(payload)

    try:
        res = requests.post(f"{API_URL}/exchange", json=payload)

        print("\n📥 RESPONSE:")
        print(res.text)

    except Exception as e:
        print("Order error:", e)

# ==============================
# MAIN
# ==============================

def run():
    print("🚀 BOT STARTED")

    send_order()

    print("\n⏳ Waiting...")

    while True:
        time.sleep(30)


if __name__ == "__main__":
    run()
