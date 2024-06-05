import json

import paypalrestsdk
import requests
from django.conf import settings

paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})  # this part for my account is not working

my_api = paypalrestsdk.Api({
    'mode': 'sandbox',
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})

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


def create_payment(amount, return_url, cancel_url):
    payment = paypalrestsdk.Payment({
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal'
        },
        'redirect_urls': {
            'return_url': return_url,
            'cancel_url': cancel_url
        },
        'transactions': [{
            'item_list': {
                'items': [{
                    'name': 'Subscription',
                    'sku': 'subscription',
                    'price': str(amount),
                    'currency': 'USD',
                    'quantity': 1
                }]
            },
            'amount': {
                'total': str(amount),
                'currency': 'USD'
            },
            'description': 'Subscription payment.'
        }]
    }, api=my_api)
    if payment.create():
        return payment
    else:
        return None


def execute_payment(payment_id, payer_id):
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({'payer_id': payer_id}):
        return payment
    else:
        return None


# def create_billing_plan(plan, return_url, cancel_url)
