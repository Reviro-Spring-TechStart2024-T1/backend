import json

import requests

from core.settings import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET


def paypal_token(
    client_id=PAYPAL_CLIENT_ID,
    client_secret=PAYPAL_CLIENT_SECRET
) -> str:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    if response.status_code == 200:
        print('Request successful!')
        access_token = json.loads(response.text)['access_token']
        print('access_token success')
        return access_token
    else:
        print('error:', response.text)
        raise
