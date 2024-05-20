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
