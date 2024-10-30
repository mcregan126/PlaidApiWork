from datetime import datetime, timedelta
import http.client
from flask import Blueprint, render_template, jsonify, send_from_directory, request, session
import http.client
import json
import os
import uuid



client_id = "65e7b7407aa8cf001cc59e7b6247f4912edd996835254c9e47bbf4"
secret = "6247f4912edd996835254c9e47bbf4"

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/get_transactions', methods=['GET'])
def get_transactions():
    
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'Access token is missing'}), 401

    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    #connect to Plaid API
    conn = http.client.HTTPSConnection("sandbox.plaid.com")
    headers = {'Content-Type': 'application/json'}

    payload = json.dumps({
        "client_id": client_id,
        "secret": secret,
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date,
        "options": {
            "count": 10,
            "offset": 0
        }
    })

    #send request to Plaid
    conn.request("POST", "/transactions/get", payload, headers)
    res = conn.getresponse()
    data = res.read()

    #parse response
    transactions_response = json.loads(data.decode("utf-8"))
    transactions = transactions_response.get('transactions', [])

    return jsonify({'transactions': transactions})

