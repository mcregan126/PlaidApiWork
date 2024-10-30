# plaid_routes.py

from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template
import http.client
import json
import os


client_id = "65e7b7407aa8cf001cc59e7b6247f4912edd996835254c9e47bbf4"
secret = "6247f4912edd996835254c9e47bbf4"

plaid_bp = Blueprint('plaid', __name__)

#create link token route
@plaid_bp.route('/create_link_token', methods=['GET'])
def create_link_token():
    if 'username' not in session:
        return redirect(url_for('users.login'))
    
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

#exchange public token for acess token
@plaid_bp.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    req_data = request.get_json()
    public_token = req_data.get('public_token')

    if not public_token:
        return jsonify({'error': 'public_token is missing'}), 400

    conn = http.client.HTTPSConnection("sandbox.plaid.com")
    headers = {'Content-Type': 'application/json'}

    payload = json.dumps({
        "client_id": client_id,
        "secret": secret,
        "public_token": public_token
    })

    conn.request("POST", "/item/public_token/exchange", payload, headers)
    res = conn.getresponse()
    data = res.read()

    exchange_response = json.loads(data.decode("utf-8"))
    access_token = exchange_response.get('access_token')

    if not access_token:
        return jsonify({'error': 'Failed to exchange public_token'}), 401

    session['access_token'] = access_token

    return jsonify({'access_token': access_token})

@plaid_bp.route('/completed', methods=['GET', 'POST'])
def completed():
    return render_template('completed.html')

