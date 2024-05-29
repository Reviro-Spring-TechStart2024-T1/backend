import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})


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
    })
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
