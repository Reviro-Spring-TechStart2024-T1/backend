import calendar
import json
import re
from datetime import datetime, timedelta
from random import choice

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
    establishment.happy_hour_start = timezone.localtime(timezone.now()).time()
    establishment.happy_hour_end = (timezone.localtime(timezone.now()) + timezone.timedelta(hours=1)).time()
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
    establishment.happy_hour_start = (timezone.localtime(timezone.now()) - timezone.timedelta(hours=2)).time()
    establishment.happy_hour_end = (timezone.localtime(timezone.now()) - timezone.timedelta(hours=1)).time()
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
    assert expected_message in error_message


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
def test_partner_customers_list_unauthorized(jwt_auth_api_client):
    client = jwt_auth_api_client(role='customer')

    url = reverse('partner-customers-list')
    response = client.get(url)

    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


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
    # when: trying to understand how many queries are sent to db
    with CaptureQueriesContext(connection) as ctx:
        url = reverse('customers-order-list-create')
        response = client.get(url)
        # then: expecting to get queries for pagination, jwtauth and the main orders'info
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
    # when: partner is using filter by status
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
    # when: partner is using filter by beverage__name
    url = reverse('partners-order-list')
    response = client.get(url, {'beverage__name': ord1.beverage.name})
    # then: expecting to get only one order with beverages name in the answer
    assert response.status_code == 200
    assert response.data['results'][0]['beverage_name'] == ord1.beverage.name


@pytest.mark.django_db
def test_get_orders_list_of_customer_using_filter_by_status(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_num_of_orders_for_one_user_from_factory
):
    # given: auth customer and a list of their orders
    customer = create_user_from_factory('customer')
    client = jwt_auth_api_client_pass_user(customer)
    orders = create_num_of_orders_for_one_user_from_factory(customer, 5)
    ord1 = orders[0]
    status1 = ord1.status
    # when: customer is using filter by status option
    url = reverse('customers-order-list-create')
    response = client.get(url, {'status': status1})
    # then: expecting to get not empty answers in results array
    assert response.status_code == 200
    assert response.data['results'] is not None
    for items in response.json()['results']:
        if items['id'] == ord1.id:
            assert items['status'] == ord1.status


@pytest.mark.django_db
def test_get_orders_list_of_customer_using_filter_by_time(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_num_of_orders_for_one_user_from_factory
):
    # given: auth customer and a list of their orders
    customer = create_user_from_factory('customer')
    client = jwt_auth_api_client_pass_user(customer)
    orders = create_num_of_orders_for_one_user_from_factory(customer, 5)
    ord1 = orders[0]
    status1 = ord1.status
    # when: customer is using filter by status option
    url = reverse('customers-order-list-create')
    response = client.get(url, {'status': status1})
    # then: expecting to get not empty answers in results array
    assert response.status_code == 200
    assert response.data['results'] is not None
    for items in response.json()['results']:
        if items['id'] == ord1.id:
            assert items['status'] == ord1.status


@pytest.mark.django_db
def test_detailed_customer_profile_non_existent(
    setup_partner_with_orders,
    jwt_auth_api_client
):
    partner, customer1, customer2 = setup_partner_with_orders
    client = jwt_auth_api_client(role='partner')
    client.force_authenticate(user=partner)
    # URL for the detailed customer profile endpoint with a non-existent customer ID
    url = reverse('detailed-customer-profile', args=[9999])
    response = client.get(url)

    # Assert the status code and response data
    assert response.status_code == 404   # not found error
    assert response.data['detail'] == 'No User matches the given query.'


@pytest.mark.django_db
def test_detailed_customer_profile_unauthorized(
    setup_partner_with_orders,
    jwt_auth_api_client
):
    partner, customer1, customer2 = setup_partner_with_orders
    client = jwt_auth_api_client(role='customer')

    # URL for the detailed customer profile endpoint
    url = reverse('detailed-customer-profile', args=[customer1.id])
    response = client.get(url)

    # Assert the status code and response data
    assert response.status_code == 403   # forbidden error
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_find_customer_by_email(
    setup_partner_with_orders,
    jwt_auth_api_client
):
    partner, customer1, customer2 = setup_partner_with_orders
    client = jwt_auth_api_client(role='partner')
    url = reverse('find-customer')

    response = client.post(url, {'email': customer1.email})

    assert response.status_code == 200
    assert response.data['email'] == customer1.email
    assert response.data['first_name'] == customer1.first_name
    assert response.data['last_name'] == customer1.last_name
    print(response.data)

    # test for non-existent email
    response = client.post(url, {'email': 'nonexistent@example.com'})
    assert response.status_code == 404   # not found error
    assert response.data['message'] == 'Customer does not exist'
    print(response.data)

    # test with an invalid email format
    response = client.post(url, {'email': 'invalid-email'})
    assert response.status_code == 400  # bad request error
    assert 'email' in response.data
    print(response.data)


@pytest.mark.django_db
def test_find_customer_by_email_unauthorized(
    setup_partner_with_orders,
    jwt_auth_api_client
):
    partner, customer1, customer2 = setup_partner_with_orders
    client = jwt_auth_api_client(role='costumer')
    url = reverse('find-customer')
    response = client.get(url, {'email': customer1.email})
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_stats_for_partner_for_one_day_as_partner(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_order_passing_bev_menu_user_at_specific_date,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth partner with est, menu bevs
    customer = create_user_from_factory('customer')
    customer1 = create_user_from_factory('customer')
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(2)
    partner = dict_data['partner']
    menu = dict_data['menu']
    bev1, bev2 = dict_data['beverages']
    today = timezone.now()
    create_order_passing_bev_menu_user_at_specific_date(
        beverage=bev1,
        menu=menu,
        user=customer,
        order_date=today
    )
    create_order_passing_bev_menu_user_at_specific_date(
        beverage=bev2,
        menu=menu,
        user=customer1,
        order_date=today
    )
    client = jwt_auth_api_client_pass_user(partner)
    # when: partner is accessing stats enpoint
    url = reverse('partner-stats')
    response = client.get(url)
    total = bev1.price + bev2.price
    # then: gets a result
    assert response.status_code == 200
    assert response.data['this_week'][today.strftime('%a-%Y-%m-%d')]['count'] == 2
    assert response.data['this_week'][today.strftime('%a-%Y-%m-%d')]['sum'] == total


@pytest.mark.django_db
def test_get_stats_for_partner_for_this_months_one_week_as_partner(
    create_num_of_users_from_factory,
    jwt_auth_api_client_pass_user,
    create_order_passing_bev_menu_user_at_specific_date,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth partner with est, menu bevs
    customers = create_num_of_users_from_factory(7)
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(2)
    partner = dict_data['partner']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    today = timezone.now() if timezone.now().day > 7 else timezone.now() + timedelta(days=7)
    this_week_start = today - timedelta(days=today.weekday())
    last_week_end = this_week_start - timedelta(days=1)
    last_week_start = last_week_end - timedelta(days=6)
    orders = [create_order_passing_bev_menu_user_at_specific_date(
        beverage=choice(beverages),
        menu=menu,
        user=choice(customers),
        order_date=last_week_start + timedelta(days=i)
    ) for i in range(7)]
    total = sum(i.beverage.price for i in orders)
    client = jwt_auth_api_client_pass_user(partner)
    # when: partner is accessing stats enpoint
    url = reverse('partner-stats')
    response = client.get(url)
    # then: gets a result
    assert response.status_code == 200
    assert response.data['this_month'][
        (str(last_week_start.strftime('%a-%Y-%m-%d')) + ' - ' +  # noqa: W504
         str(last_week_end.strftime('%a-%Y-%m-%d')))]['count'] == 7
    assert response.data['this_month'][
        (str(last_week_start.strftime('%a-%Y-%m-%d')) + ' - ' +  # noqa: W504
         str(last_week_end.strftime('%a-%Y-%m-%d')))]['sum'] == total


@pytest.mark.django_db
def test_get_stats_for_partner_for_last_quarters_last_month_as_partner(
    create_num_of_users_from_factory,
    jwt_auth_api_client_pass_user,
    create_order_passing_bev_menu_user_at_specific_date,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth partner with est, menu bevs
    customers = create_num_of_users_from_factory(7)
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(2)
    partner = dict_data['partner']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    today = timezone.now() + timedelta(days=7) if timezone.now().day < 7 else timezone.now()
    this_quarter_start_month = (today.month - 1) // 3 * 3 + 1
    previous_quarter_end_month = (today.year - 1, 12, 1) if this_quarter_start_month == 1 else (
        datetime(today.year, this_quarter_start_month, 1, tzinfo=today.tzinfo) - timedelta(days=1)).replace(day=1)
    _, prev_quarter_end_month_days_range = calendar.monthrange(
        previous_quarter_end_month.year, previous_quarter_end_month.month)
    orders = [create_order_passing_bev_menu_user_at_specific_date(
        beverage=choice(beverages),
        menu=menu,
        user=choice(customers),
        order_date=previous_quarter_end_month + timedelta(days=i)
    ) for i in range(prev_quarter_end_month_days_range)]
    total = sum(i.beverage.price for i in orders)
    client = jwt_auth_api_client_pass_user(partner)
    # when: partner is accessing stats enpoint
    url = reverse('partner-stats')
    response = client.get(url)
    # then: gets a result
    assert response.status_code == 200
    assert response.data['last_quarter'][previous_quarter_end_month.strftime(
        '%Y-%m')]['count'] == prev_quarter_end_month_days_range
    assert response.data['last_quarter'][previous_quarter_end_month.strftime('%Y-%m')]['sum'] == total


@pytest.mark.django_db
def test_get_stats_for_partner_for_last_year_as_partner(
    create_num_of_users_from_factory,
    jwt_auth_api_client_pass_user,
    create_order_passing_bev_menu_user_at_specific_date,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth partner with est, menu bevs
    customers = create_num_of_users_from_factory(36)
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(2)
    partner = dict_data['partner']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    today = timezone.now()
    last_year_start = datetime(today.year - 1, 1, 1, tzinfo=today.tzinfo)
    last_year_end = datetime(today.year - 1, 12, 31, 23, 59, 59, tzinfo=today.tzinfo)
    last_year_days = (last_year_end - last_year_start).days + 1
    last_year = today.year - 1
    orders = [create_order_passing_bev_menu_user_at_specific_date(
        beverage=choice(beverages),
        menu=menu,
        user=choice(customers),
        order_date=last_year_start + timedelta(days=i)
    ) for i in range(last_year_days)]
    quarters = {
        'Q1': {
            'start': datetime(last_year, 1, 1, tzinfo=today.tzinfo),
            'end': datetime(last_year, 3, 31, 23, 59, 59, tzinfo=today.tzinfo)
        },
        'Q2': {
            'start': datetime(last_year, 4, 1, tzinfo=today.tzinfo),
            'end': datetime(last_year, 6, 30, 23, 59, 59, tzinfo=today.tzinfo)
        },
        'Q3': {
            'start': datetime(last_year, 7, 1, tzinfo=today.tzinfo),
            'end': datetime(last_year, 9, 30, 23, 59, 59, tzinfo=today.tzinfo)
        },
        'Q4': {
            'start': datetime(last_year, 10, 1, tzinfo=today.tzinfo),
            'end': datetime(last_year, 12, 31, 23, 59, 59, tzinfo=today.tzinfo)
        }
    }
    Q1_days = (quarters['Q1']['end'] - quarters['Q1']['start']).days + 1
    Q2_days = (quarters['Q2']['end'] - quarters['Q2']['start']).days + 1
    Q3_days = (quarters['Q3']['end'] - quarters['Q3']['start']).days + 1
    Q4_days = (quarters['Q4']['end'] - quarters['Q4']['start']).days + 1
    Q1_total = [orders[i].beverage.price for i in range(Q1_days)]
    Q2_total = [orders[i].beverage.price for i in range(Q1_days, Q1_days + Q2_days)]
    Q3_total = [orders[i].beverage.price for i in range((Q1_days + Q2_days), Q1_days + Q2_days + Q3_days)]
    Q4_total = [orders[i].beverage.price for i in range(
        (Q1_days + Q2_days + Q3_days), (Q1_days + Q2_days + Q3_days + Q4_days))]
    total_counts = [len(Q1_total), len(Q2_total), len(Q3_total), len(Q4_total)]
    total_sums = [sum(Q1_total), sum(Q2_total), sum(Q3_total), sum(Q4_total)]
    client = jwt_auth_api_client_pass_user(partner)
    # when: partner is accessing stats enpoint
    url = reverse('partner-stats')
    response = client.get(url)
    # then: gets a result
    assert response.status_code == 200
    for i in range(1, 5):
        assert response.data['last_year'][f'Q{i}_{last_year}']['count'] == total_counts[i - 1]
        assert response.data['last_year'][f'Q{i}_{last_year}']['sum'] == total_sums[i - 1]
