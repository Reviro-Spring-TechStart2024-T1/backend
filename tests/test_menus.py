import json

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_post_menu_as_customer(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='customer')
    est = create_establishment_from_factory
    menu_post_data = {
        'establishment': est.id
    }
    # when:
    url = reverse('menu-list')
    response = client.post(
        url,
        data=json.dumps(menu_post_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_post_menu_as_partner(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    est = create_establishment_from_factory
    menu_post_data = {
        'establishment': est.id
    }
    # when:
    url = reverse('menu-list')
    response = client.post(
        url,
        data=json.dumps(menu_post_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['establishment'] == est.id


@pytest.mark.django_db
def test_get_menu_with_no_beverages_as_customer(
    jwt_auth_api_client,
    create_menu_from_factory
):
    # given:
    client = jwt_auth_api_client(role='customer')
    menu = create_menu_from_factory
    # when:
    url = reverse('menu-detail', args=[menu.id])
    response = client.get(url)
    print(response.json())
    # then:
    assert response.status_code == 200
    assert response.data['id'] == menu.id
    assert response.data['beverages'] == []


@pytest.mark.django_db
def test_get_menu_with_no_beverages_as_partner(
    jwt_auth_api_client,
    create_menu_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    menu = create_menu_from_factory
    # when:
    url = reverse('menu-detail', args=[menu.id])
    response = client.get(url)
    print(response.json())
    # then:
    assert response.status_code == 200
    assert response.data['id'] == menu.id
    assert response.data['beverages'] == []


@pytest.mark.django_db
def test_get_menu_with_beverages_as_partner(
    jwt_auth_api_client,
    create_num_of_beverages_in_one_menu_from_outside_factory,
    create_menu_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    menu = create_menu_from_factory
    beverages = create_num_of_beverages_in_one_menu_from_outside_factory(menu, 3)
    # when:
    url = reverse('menu-detail', args=[menu.id])
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['id'] == menu.id
    assert response.data['beverages'] != []
    assert len(response.data['beverages']) == len(beverages)


@pytest.mark.django_db
def test_get_menu_with_beverages_as_customer_filter_by_beverage_name(
    create_partner_establishment_menu_and_num_of_beverages_as_dict,
    jwt_auth_api_client
):
    # given: auth customer and menu with num of beverages
    client = jwt_auth_api_client('customer')
    data_dict = create_partner_establishment_menu_and_num_of_beverages_as_dict(15)
    menu = data_dict['menu']
    beverages = data_dict['beverages']
    last_bev = beverages[-1]
    # when: customer filters menu by the name of beverage
    url = reverse('menu-detail', args=[menu.id])
    response = client.get(url, {'beverage__name': last_bev.name})
    # then: expecting the result to contain/filter beverages
    assert response.status_code == 200
    assert response.data['beverages'][0]['name'] == last_bev.name


@pytest.mark.django_db
def test_delete_beverage_not_seen_in_all_parts_by_partner(
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth partner with est, menu and bevs
    num_of_bevs = 7
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(num_of_bevs)
    partner = dict_data['partner']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    bev4 = beverages[3]
    client = jwt_auth_api_client_pass_user(partner)
    # when: partner deletes the bev4 from their menu
    delete_url = reverse('beverage-detail', args=[bev4.id])
    delete_response = client.delete(delete_url)
    # then: expecting bev4 not to be present in any place where the beverages have to be present
    assert delete_response.status_code == 204
    assert delete_response.data is None
    check_detail_url = reverse('beverage-detail', args=[bev4.id])
    check_detail_response = client.get(check_detail_url)
    assert check_detail_response.status_code == 404
    assert check_detail_response.data['detail'] == 'No Beverage matches the given query.'
    check_list_url = reverse('beverage-list')
    check_list_response = client.get(check_list_url)
    assert len(check_list_response.data['results']) == num_of_bevs - 1
    check_menu_detail_url = reverse('menu-detail', args=[menu.id])
    check_menu_detail_response = client.get(check_menu_detail_url)
    assert check_menu_detail_response.status_code == 200
    assert len(check_menu_detail_response.data['beverages']) == num_of_bevs - 1
    check_menu_list_url = reverse('menu-list')
    check_menu_list_response = client.get(check_menu_list_url)
    print('check_menu_list_response:', check_menu_list_response.data)
    assert len(check_menu_list_response.data['results'][0]['beverages']) == num_of_bevs - 1


@pytest.mark.django_db
def test_delete_beverage_not_seen_in_all_parts_by_customer(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth partner with est, menu and bevs deletes bev and auth customer
    customer = create_user_from_factory('customer')
    num_of_bevs = 7
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(num_of_bevs)
    partner = dict_data['partner']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    bev4 = beverages[3]
    partner_client = jwt_auth_api_client_pass_user(partner)
    customer_client = jwt_auth_api_client_pass_user(customer)
    # when: partner deletes the bev4 from their menu
    delete_url = reverse('beverage-detail', args=[bev4.id])
    delete_response = partner_client.delete(delete_url)
    # then: expecting bev4 not to be present in any place where the beverages have to be present
    assert delete_response.status_code == 204
    assert delete_response.data is None
    check_detail_url = reverse('beverage-detail', args=[bev4.id])
    check_detail_response = customer_client.get(check_detail_url)
    assert check_detail_response.status_code == 404
    assert check_detail_response.data['detail'] == 'No Beverage matches the given query.'
    check_list_url = reverse('beverage-list')
    check_list_response = customer_client.get(check_list_url)
    assert len(check_list_response.data['results']) == num_of_bevs - 1
    check_menu_detail_url = reverse('menu-detail', args=[menu.id])
    check_menu_detail_response = customer_client.get(check_menu_detail_url)
    print('check_menu_detail_response:', check_menu_detail_response.data)
    assert check_menu_detail_response.status_code == 200
    assert len(check_menu_detail_response.data['beverages']) == num_of_bevs - 1
