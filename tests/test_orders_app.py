import json
import re

import pytest
from django.utils import timezone
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_history_customer_orders(
    jwt_auth_api_user_and_client,
    create_num_of_orders_for_one_user_from_factory,
    create_user_from_factory
):
    # given: authenticated customer and existing orders
    user, client = jwt_auth_api_user_and_client(role='customer')
    orders = create_num_of_orders_for_one_user_from_factory(user=user, num=7)

    # when:
    url = reverse('customers-order-list-create')
    response = client.get(url)

    # then:
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()['results']) == len(orders)


@pytest.mark.django_db
def test_create_order_during_happy_hours_as_customer(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given: authenticated customer and a beverage during happy hours
    client = jwt_auth_api_client(role='customer')
    beverage = create_beverage_from_factory
    establishment = beverage.menu.establishment
    establishment.happy_hour_start = timezone.now().time()
    establishment.happy_hour_end = (timezone.now() + timezone.timedelta(hours=1)).time()
    establishment.save()

    order_data = {'beverage_id': beverage.id}
    # when:
    url = reverse('customers-order-list-create')
    response = client.post(
        url,
        data=json.dumps(order_data),
        content_type='application/json'
    )
    # then:
    print(response.json())
    assert response.status_code == 201
    assert response.json()['beverage_name'] == beverage.name


@pytest.mark.django_db
def test_create_order_outside_happy_hours_as_customer(
    jwt_auth_api_client,
    create_user_from_factory,
    create_beverage_from_factory
):
    # given: authenticated customer and a beverage outside happy hours
    client = jwt_auth_api_client(role='customer')
    beverage = create_beverage_from_factory
    establishment = beverage.menu.establishment
    establishment.happy_hour_start = (timezone.now() - timezone.timedelta(hours=2)).time()
    establishment.happy_hour_end = (timezone.now() - timezone.timedelta(hours=1)).time()
    establishment.save()

    order_data = {'beverage_id': beverage.id}
    # when:
    url = reverse('customers-order-list-create')
    response = client.post(
        url,
        data=json.dumps(order_data),
        content_type='application/json'
    )
    print(response.json().get('error'))
    # then:
    assert response.status_code == 400
    error_response = response.json()['error']
    match = re.search(r"ErrorDetail\(string='([^']*)'", error_response)
    error_message = match.group(1) if match else None
    expected_message = 'It is not happy hour currently. Please order within establishment happy hours'
    assert error_message == expected_message


@pytest.mark.django_db
def test_retrieve_order_as_partner(
    jwt_auth_api_user_and_client,
    create_order_from_factory
):
    # given: authenticated partner and an existing order
    user, client = jwt_auth_api_user_and_client(role='partner')
    order = create_order_from_factory
    order.beverage.menu.establishment.owner = user
    order.beverage.menu.establishment.save()
    # when:
    url = reverse('partners-order-detail', args=[order.id])
    response = client.get(url)
    # then:
    print(response.json())
    assert response.status_code == 200
    assert response.json()['id'] == order.id


@pytest.mark.django_db
def test_update_order_status_as_partner(
    jwt_auth_api_user_and_client,
    create_user_from_factory,
    create_order_from_factory
):
    # given: authenticated partner and an existing order
    user, client = jwt_auth_api_user_and_client(role='partner')
    order = create_order_from_factory
    order.beverage.menu.establishment.owner = user
    order.beverage.menu.establishment.save()
    update_data = {'status': 'cancelled'}
    # when:
    url = reverse('partners-order-detail', args=[order.id])
    response = client.patch(
        url,
        data=json.dumps(update_data),
        content_type='application/json'
    )
    # then:
    print(response.json())
    assert response.status_code == 200
    assert response.json()['status'] == 'cancelled'
