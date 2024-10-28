from datetime import datetime, timedelta
import http.client
from flask import Flask, render_template, jsonify, send_from_directory, request, session
import http.client
import json
import os
import uuid

app = Flask(__name__)

client_id = "65e7b7407aa8cf001cc59e7b6247f4912edd996835254c9e47bbf4"
secret = "6247f4912edd996835254c9e47bbf4"




@app.route('/get_transactions', methods=['GET'])
def get_transactions():
   
    # get from session
    access_token = session['access_token']
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

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

    conn.request("POST", "/transactions/get", payload, headers)
    res = conn.getresponse()
    data = res.read()

    transactions_response = json.loads(data.decode("utf-8"))
    transactions = transactions_response.get('transactions', [])

    return jsonify({'transactions': transactions})
