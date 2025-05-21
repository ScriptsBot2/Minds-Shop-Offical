from flask import Flask, request, jsonify, render_template
import json
import datetime
import requests

app = Flask(__name__)

KEYS_FILE = 'keys.json'
WEBHOOK_URL = 'https://discord.com/api/webhooks/1374804860834418779/H16-C9MLeuQ43iU7bh1uGZEz7kzw-_Pt0m9MFZWfoZZoEql8NpXLe6qJAlhCUqcnrsW8'

try:
    with open(KEYS_FILE, 'r') as f:
        keys_db = json.load(f)
except FileNotFoundError:
    keys_db = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redeem', methods=['POST'])
def redeem():
    data = request.get_json()
    code = data.get('code', '').strip()
    if not code:
        return jsonify(success=False, message="No code provided"), 400

    if code not in keys_db:
        return jsonify(success=False, message="Invalid gift card code"), 400
    if keys_db[code].get('used', False):
        return jsonify(success=False, message="Code already redeemed"), 400

    keys_db[code]['used'] = True
    keys_db[code]['redeemed_at'] = datetime.datetime.utcnow().isoformat()

    with open(KEYS_FILE, 'w') as f:
        json.dump(keys_db, f, indent=2)

    try:
        requests.post(WEBHOOK_URL, json={
            "username": "Key Logs",
            "content": f"Giftcard code **{code}** was redeemed."
        })
    except Exception as e:
        print(f"Webhook failed: {e}")

    return jsonify(success=True, message="Code redeemed successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
