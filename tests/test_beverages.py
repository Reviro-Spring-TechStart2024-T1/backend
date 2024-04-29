import json

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_get_list_of_beverages_as_customer(
    jwt_auth_api_client,
    create_num_of_beverages_in_one_menu_from_factories
):
    # given:
    client = jwt_auth_api_client('customer')
    five_beverages = create_num_of_beverages_in_one_menu_from_factories(5)
    # when:
    url = reverse('beverage-list')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.json()) == len(five_beverages)


@pytest.mark.django_db
def test_get_list_of_beverages_as_partner(
    jwt_auth_api_client,
    create_num_of_beverages_in_one_menu_from_factories
):
    # given:
    client = jwt_auth_api_client('partner')
    five_beverages = create_num_of_beverages_in_one_menu_from_factories(5)
    # when:
    url = reverse('beverage-list')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.json()) == len(five_beverages)


@pytest.mark.django_db
def test_post_of_beverages_as_customer(
    jwt_auth_api_client,
    create_menu_from_factory,
    create_category_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    menu = create_menu_from_factory
    category = create_category_from_factory
    item_data = {
        'menu': menu.id,
        'name': 'tea',
        'item_category': category.id,
        'price': '99.99',
        'description': 'Nice tea',
        'in_stock': 50
    }
    # when:
    url = reverse('beverage-list')
    response = client.post(
        url,
        data=json.dumps(item_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_post_of_beverages_as_partner(
    jwt_auth_api_client,
    create_menu_from_factory,
    create_category_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    menu = create_menu_from_factory
    category = create_category_from_factory
    item_data = {
        'menu': menu.id,
        'name': 'tea',
        'category': category.id,
        'price': '99.99',
        'description': 'Nice tea',
        'in_stock': 50
    }
    # when:
    url = reverse('beverage-list')
    response = client.post(
        url,
        data=json.dumps(item_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 201
    assert response.data['menu'] == menu.id
    assert response.data['name'] == item_data['name']
    assert response.data['category'] == category.id
    assert response.data['price'] == item_data['price']
    assert response.data['description'] == item_data['description']
    assert response.data['in_stock'] == item_data['in_stock']


@pytest.mark.django_db
def test_get_beverage_as_partner(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    item = create_beverage_from_factory
    # when:
    url = reverse('beverage-detail', args=[item.id])
    response = client.get(
        url
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['name'] == item.name
    assert response.data['price'] == str(item.price)
    assert response.data['description'] == item.description
    assert response.data['in_stock'] == item.in_stock


@pytest.mark.django_db
def test_get_beverage_as_customer(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    item = create_beverage_from_factory
    # when:
    url = reverse('beverage-detail', args=[item.id])
    response = client.get(
        url
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['name'] == item.name
    assert response.data['price'] == str(item.price)
    assert response.data['description'] == item.description
    assert response.data['in_stock'] == item.in_stock


@pytest.mark.django_db
def test_patch_beverage_as_partner(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    item = create_beverage_from_factory
    patch_data = {
        'name': 'apple juice',
        'description': 'best apple juice'
    }
    # when:
    url = reverse('beverage-detail', args=[item.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['name'] == patch_data['name']
    assert response.data['description'] == patch_data['description']
    assert response.data['price'] == str(item.price)
    assert response.data['in_stock'] == item.in_stock


@pytest.mark.django_db
def test_patch_beverage_as_customer(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    item = create_beverage_from_factory
    patch_data = {
        'name': 'apple juice',
        'description': 'best apple juice'
    }
    # when:
    url = reverse('beverage-detail', args=[item.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_delete_beverage_as_partner(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    item = create_beverage_from_factory
    # when:
    url = reverse('beverage-detail', args=[item.id])
    response = client.delete(
        url
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_delete_beverage_as_customer(
    jwt_auth_api_client,
    create_beverage_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    item = create_beverage_from_factory
    # when:
    url = reverse('beverage-detail', args=[item.id])
    response = client.delete(
        url
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'
