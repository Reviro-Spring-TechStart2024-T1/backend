import json

import requests

# reason for hard coding keys is in that when getting token from PayPal the .env variables were passed as null
# TODO: research and dea with this bug (maybe try using export to computers env's)
PAYPAL_CLIENT_ID = 'ARwvbKUESLbr9ezp2xr66HPo9KYSZU71pl3TkuRqcy9YAJCxCJTpF15Xzyd4IAlEQ_oPZm10QXw35tMs'
PAYPAL_CLIENT_SECRET = 'EMC1rq0KXwC2PvKyWvpz6Nc9gfjKRUJgzBZkPEFxfCAD2Lp7R821EiJAchG3IxDm55OtZv1DkESymeLd'


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
