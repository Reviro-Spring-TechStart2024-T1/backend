import json
import re

import pytest
import pytz
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.reverse import reverse

from orders.models import Order


@pytest.mark.django_db
def test_history_customer_orders(
    jwt_auth_api_user_and_client,
    create_num_of_orders_for_one_user_from_factory,
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


@pytest.mark.django_db
def test_partner_customers_list(
    jwt_auth_api_client,
    setup_partner_with_orders
):
    partner, customer1, customer2 = setup_partner_with_orders
    client = jwt_auth_api_client(role='partner')
    client.force_authenticate(user=partner)
    url = reverse('partner-customers-list')
    response = client.get(url)

    print(response.data)
    assert response.status_code == 200
    assert len(response.data['results']) == 2  # for partner to see all his customers

    # Test searching by email
    response = client.get(url, {'search': customer1.email})
    print(response.data['results'])
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['email'] == customer1.email


@pytest.mark.django_db
def test_detailed_customer_profile(
    setup_partner_with_orders,
    jwt_auth_api_client
):
    partner, customer1, customer2 = setup_partner_with_orders
    client = jwt_auth_api_client(role='partner')
    client.force_authenticate(user=partner)
    url = reverse('detailed-customer-profile', args=[customer1.id])
    response = client.get(url)

    # Assert the status code and response data
    assert response.status_code == 200
    assert response.data['email'] == customer1.email
    assert 'orders' in response.data
    assert len(response.data['orders']) == 3  # 3 orders were created for customer1

    # Check details of orders
    for order in response.data['orders']:
        assert 'id' in order
        assert 'order_date' in order
        assert 'beverage_name' in order
        assert 'price' in order

    print(f'Total orders of customer1: {Order.objects.filter(user=customer1).count()}')
    print(f'Total orders of customer2 associated with the partner: '
          f'{Order.objects.filter(user=customer2, beverage__menu__establishment__owner=partner).count()}')
    print(response.data)


@pytest.mark.djnago_db
def test_num_of_queries_sent_to_db_to_get_list_of_orders_as_customer(
    create_num_of_orders_for_one_user_from_factory,
    jwt_auth_api_user_and_client
):
    # given: authenticated user who is accessing their order history
    user, client = jwt_auth_api_user_and_client('customer')
    create_num_of_orders_for_one_user_from_factory(user, 20)
    query_get_users_from_jwt = 1
    query_get_count_for_paginated_result = 1
    query_to_get_all_orders_of_the_user_for_orders_history = 1
    sum_of_queries = sum((query_get_count_for_paginated_result, query_get_users_from_jwt,
                         query_to_get_all_orders_of_the_user_for_orders_history))
    # when:
    with CaptureQueriesContext(connection) as ctx:
        url = reverse('customers-order-list-create')
        response = client.get(url)
        # then:
        assert response.status_code == 200
        print(ctx.captured_queries)
        assert len(ctx) == sum_of_queries

# @pytest.mark.djnago_db
# def test_num_of_queries_sent_to_db_to_get_list_of_orders_as_partner(
#     create_num_of_orders_for_one_user_from_factory,
#     jwt_auth_api_user_and_client,
#     create_user_from_factory
# ):
#     # given: authenticated user who is accessing their order history
#     user, client = jwt_auth_api_user_and_client('partner')
#     customer = create_user_from_factory
#     create_num_of_orders_for_one_user_from_factory(customer, 5)
#     query_get_users_from_jwt = 1
#     query_get_count_for_paginated_result = 1
#     query_to_get_all_orders_of_the_user_for_orders_history = 1
#     sum_of_queries = sum((query_get_count_for_paginated_result, query_get_users_from_jwt, query_to_get_all_orders_of_the_user_for_orders_history))
#     # when:
#     with CaptureQueriesContext(connection) as ctx:
#         url = reverse('partners-order-list')
#         response = client.get(url)
#         # then:
#         assert response.status_code == 200
#         print(ctx.captured_queries)
#         assert len(ctx) == sum_of_queries


@pytest.mark.django_db
def test_get_partners_orders_lists_id_filter_as_partner(
    create_order_for_specific_beverage_from_factory,
    create_partner_establishment_menu_and_num_of_beverages_as_dict,
    jwt_auth_api_client_pass_user
):
    # given: authenticated partner with establishment menu and some beverages of that menu
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(5)
    partner = dict_data['partner']
    beverages = dict_data['beverages']
    bev1, bev2, bev3, bev4, bev5 = beverages
    client = jwt_auth_api_client_pass_user(partner)
    ord1 = create_order_for_specific_beverage_from_factory(bev1)
    create_order_for_specific_beverage_from_factory(bev2)
    create_order_for_specific_beverage_from_factory(bev3)
    create_order_for_specific_beverage_from_factory(bev4)
    ord5 = create_order_for_specific_beverage_from_factory(bev5)
    # when: partner is using filter by id
    url = reverse('partners-order-list')
    response = client.get(url, {'id': ord1.id})
    # then: expecting to get only that one order
    assert response.status_code == 200
    assert response.data['results'][0]['id'] == ord1.id
    url = reverse('partners-order-list')
    # when: partner is using filter for other order by id
    response = client.get(url, {'id': ord5.id})
    # then: expecting to get only that one order
    assert response.status_code == 200
    assert response.data['results'][0]['id'] == ord5.id


@pytest.mark.django_db
def test_get_partners_orders_lists_order_date_filter_as_partner(
    create_order_for_specific_beverage_from_factory,
    create_partner_establishment_menu_and_num_of_beverages_as_dict,
    jwt_auth_api_client_pass_user
):
    # given: authenticated partner with establishment menu and some beverages of that menu
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(5)
    partner = dict_data['partner']
    beverages = dict_data['beverages']
    bev1 = beverages[0]
    client = jwt_auth_api_client_pass_user(partner)
    ord1 = create_order_for_specific_beverage_from_factory(bev1)
    tz_bishkek = pytz.timezone('Asia/Bishkek')
    aware_datetime = tz_bishkek.localize(ord1.order_date)
    # when: partner is using filter by order_date
    url = reverse('partners-order-list')
    response = client.get(url, {'order_date': str(ord1.order_date)[:10]})
    # then: expecting to get only first order in the answer
    assert response.status_code == 200
    assert response.data['results'][0]['order_date'] == str(aware_datetime.isoformat())


@pytest.mark.django_db
def test_get_partners_orders_lists_status_filter_as_partner(
    create_order_for_specific_beverage_from_factory,
    create_partner_establishment_menu_and_num_of_beverages_as_dict,
    jwt_auth_api_client_pass_user
):
    # given: authenticated partner with establishment menu and some beverages of that menu
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(5)
    partner = dict_data['partner']
    beverages = dict_data['beverages']
    bev1 = beverages[0]
    client = jwt_auth_api_client_pass_user(partner)
    ord1 = create_order_for_specific_beverage_from_factory(bev1)
    # when: partner is using filter by order_date
    url = reverse('partners-order-list')
    response = client.get(url, {'status': ord1.status})
    # then: expecting to get only first order in the answer
    assert response.status_code == 200
    assert response.data['results'][0]['status'] == ord1.status


@pytest.mark.django_db
def test_get_partners_orders_lists_beverage_name_filter_as_partner(
    create_order_for_specific_beverage_from_factory,
    create_partner_establishment_menu_and_num_of_beverages_as_dict,
    jwt_auth_api_client_pass_user
):
    # given: authenticated partner with establishment menu and some beverages of that menu
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(5)
    partner = dict_data['partner']
    beverages = dict_data['beverages']
    bev1 = beverages[0]
    client = jwt_auth_api_client_pass_user(partner)
    ord1 = create_order_for_specific_beverage_from_factory(bev1)
    # when: partner is using filter by order_date
    url = reverse('partners-order-list')
    response = client.get(url, {'beverage__name': ord1.beverage.name})
    # then: expecting to get only first order in the answer
    assert response.status_code == 200
    assert response.data['results'][0]['beverage_name'] == ord1.beverage.name
