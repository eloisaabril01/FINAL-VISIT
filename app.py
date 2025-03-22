from flask import Flask, jsonify
import aiohttp
import asyncio
import json
import os

app = Flask(__name__)

# Fetch the first 4 valid tokens from ind_tokens.json
def fetch_tokens():
    try:
        with open("ind_tokens.json", "r") as file:
            tokens_data = json.load(file)
            print("🔹 Retrieved data from ind_tokens.json:", tokens_data)  # ✅ Log data for verification

            # Extract the list of tokens
            tokens = [item["token"] for item in tokens_data if "token" in item]
            
            # Take only the first 4 valid tokens
            valid_tokens = tokens[:4]

            print(f"✅ Extracted {len(valid_tokens)} valid tokens: {valid_tokens}")
            return valid_tokens
    except Exception as e:
        print(f"⚠️ Error while fetching tokens: {e}")
        return []

# Send requests
async def visit(session, token, uid, data):
    url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
    headers = {
        'X-Unity-Version': '2018.4.11f1',
        'ReleaseVersion': 'OB48',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-GA': 'v1 1',
        'Authorization': f'Bearer {token}',
        'Content-Length': '16',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
        'Host': 'client.ind.ggblueshark.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    try:
        async with session.post(url, headers=headers, data=data, ssl=False):
            pass  # Ignore response
    except:
        pass  # Ignore errors

# Send requests at maximum speed
async def send_requests_concurrently(tokens, uid, num_requests=50):
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        data = bytes.fromhex(encrypt_api(f"08{Encrypt_ID(uid)}1007"))
        tasks = [asyncio.create_task(visit(session, tokens[i % len(tokens)], uid, data)) for i in range(num_requests)]
        await asyncio.gather(*tasks)

@app.route('/<int:uid>', methods=['GET'])
def send_visits(uid):
    tokens = fetch_tokens()
    
    if not tokens:
        return jsonify({"message": "⚠️ No valid token found"}), 500
    
    print(f"✅ Available tokens count: {len(tokens)}")  # ✅ Confirm token count

    num_requests = 50
    asyncio.run(send_requests_concurrently(tokens, uid, num_requests))

    return jsonify({"message": f"✅ Sent {num_requests} visitors to UID: {uid} using {len(tokens)} tokens at high speed"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
