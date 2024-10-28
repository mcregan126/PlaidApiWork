
from flask import Flask, render_template, jsonify, send_from_directory, request, session
import http.client
import json
import os
import uuid

app = Flask(__name__)

client_id = "65e7b7407aa8cf001cc59e7b6247f4912edd996835254c9e47bbf4"
secret = "6247f4912edd996835254c9e47bbf4"

# string of 24 random bytes
app.secret_key = os.urandom(24)  
user_id = "fix"



@app.route('/completed')
def completed():
    return send_from_directory('.', 'completed.html')



# Route to create the link token
@app.route('/create_link_token', methods=['GET'])
def create_link_token():
    conn = http.client.HTTPSConnection("sandbox.plaid.com")
    headers = {'Content-Type': 'application/json'}

    payload = json.dumps({
  "client_id": "65e7b7407aa8cf001cc59e7b",
  "secret": "6247f4912edd996835254c9e47bbf4",
  "client_name": "InnoBank user",
  "country_codes": [
    "US"
  ],
  "language": "en",
  "user": {
    "client_user_id": "unique_user_id"
  },
  "products": [
    "auth"
  ]
})

    conn.request("POST", "/link/token/create", payload, headers)
    res = conn.getresponse()
    data = res.read()

    link_token_response = json.loads(data.decode("utf-8"))
    link_token = link_token_response['link_token']

    return jsonify({'link_token': link_token})



# Route to exchange public_token for access_token
@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    req_data = request.get_json()
    public_token = req_data.get('public_token')

    if not public_token:
        return jsonify({'error': 'public_token is missing'}), 400

    conn = http.client.HTTPSConnection("sandbox.plaid.com")
    headers = {'Content-Type': 'application/json'}

    payload = json.dumps({
        "client_id": "65e7b7407aa8cf001cc59e7b",
        "secret": "6247f4912edd996835254c9e47bbf4",
        "public_token": public_token
    })

    conn.request("POST", "/item/public_token/exchange", payload, headers)
    res = conn.getresponse()
    data = res.read()

    exchange_response = json.loads(data.decode("utf-8"))
    access_token = exchange_response.get('access_token')

    if not access_token:
        return jsonify({'error': 'Failed to exchange public_token'}), 401

    session['user_id'] = user_id 
    session['access_token'] = access_token

    return jsonify({'access_token': access_token})

# Serve the frontend HTML
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'frontend.html')

if __name__ == '__main__':
    app.run(debug=True)
