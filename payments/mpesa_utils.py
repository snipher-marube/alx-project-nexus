import os
import base64
import requests
from datetime import datetime
from decouple import config

def get_mpesa_access_token():
    consumer_key = config('CONSUMER_KEY')
    consumer_secret = config('CONSUMER_SECRET')
    api_url = f"{config('MPESA_BASE_URL')}/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json()['access_token']
    return None

def get_lipa_na_mpesa_password(shortcode, passkey):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = f"{shortcode}{passkey}{timestamp}"
    password_bytes = password_str.encode('utf-8')
    return base64.b64encode(password_bytes).decode('utf-8')

def initiate_stk_push(phone_number, amount, order_id, shortcode, passkey, callback_url):
    access_token = get_mpesa_access_token()
    if not access_token:
        return None

    api_url = f"{config('MPESA_BASE_URL')}/mpesa/stkpush/v1/processrequest"
    password = get_lipa_na_mpesa_password(shortcode, passkey)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": order_id,
        "TransactionDesc": f"Payment for order {order_id}"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
