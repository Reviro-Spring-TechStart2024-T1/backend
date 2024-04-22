import json

import pytest
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import AccessToken

from menu.models import ItemCategory


@pytest.mark.django_db
def test_get_list_of_item_categories_for_unauth_user(
    unauth_api_client,
    create_num_of_item_categories_in_array
):
    # given:
    client = unauth_api_client
    number_of_categories = 5
    categories = create_num_of_item_categories_in_array(number_of_categories)
    # when:
    url = reverse('item-category-list')
    response = client.get(url)
    # print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.json()) == number_of_categories
    assert response.json()[0]['name'] == categories[0].name
    assert response.json()[1]['name'] == categories[1].name
    assert response.json()[2]['name'] == categories[2].name
    assert response.json()[3]['name'] == categories[3].name
    assert response.json()[4]['name'] == categories[4].name


@pytest.mark.django_db
def test_get_list_of_item_categories_for_auth_user(
    jwt_auth_api_client,
    create_num_of_item_categories_in_array
):
    # given:
    client = jwt_auth_api_client
    number_of_categories = 5
    categories = create_num_of_item_categories_in_array(number_of_categories)
    # when:
    url = reverse('item-category-list')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.json()) == number_of_categories
    assert response.json()[0]['name'] == categories[0].name
    assert response.json()[1]['name'] == categories[1].name
    assert response.json()[2]['name'] == categories[2].name
    assert response.json()[3]['name'] == categories[3].name
    assert response.json()[4]['name'] == categories[4].name


@pytest.mark.django_db
def test_create_item_category_as_admin(
    admin_user,
    unauth_api_client
):
    # given: a superuser
    token = AccessToken.for_user(admin_user)
    client = unauth_api_client
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
    # when: executing POST operation to create category
    cat_name = {
        'name': 'milkshakes'
    }
    url = reverse('item-category-list')
    response = client.post(
        url,
        data=json.dumps(cat_name),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['name'] == cat_name['name']


@pytest.mark.django_db
def test_create_item_category_as_user(
    jwt_auth_api_client
):
    # given: a standart user
    client = jwt_auth_api_client
    # when: executing POST operation to create category
    cat_name = {
        'name': 'milkshakes'
    }
    url = reverse('item-category-list')
    response = client.post(
        url,
        data=json.dumps(cat_name),
        content_type='application/json'
    )
    # print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_retrieve_item_category_as_admin(
    admin_user,
    unauth_api_client,
    create_num_of_item_categories_in_array
):
    # given: a superuser and some categories
    categories = create_num_of_item_categories_in_array(5)
    token = AccessToken.for_user(admin_user)
    client = unauth_api_client
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
    # when:
    url = reverse('item-category-detail', args=[categories[0].id])
    response = client.get(
        url
    )
    # then:
    assert response.status_code == 200
    assert response.data['name'] == categories[0].name


@pytest.mark.django_db
def test_retrieve_item_category_as_user(
    jwt_auth_api_client,
    create_num_of_item_categories_in_array
):
    # given: a superuser and some categories
    categories = create_num_of_item_categories_in_array(5)
    client = jwt_auth_api_client
    # when:
    url = reverse('item-category-detail', kwargs={'pk': categories[0].id})
    response = client.get(
        url
    )
    # then:
    assert response.status_code == 200
    assert response.data['name'] == categories[0].name


@pytest.mark.django_db
def test_patch_item_category_as_admin(
    admin_user,
    unauth_api_client,
    create_num_of_item_categories_in_array
):
    # given: a superuser and some categories
    categories = create_num_of_item_categories_in_array(5)
    token = AccessToken.for_user(admin_user)
    client = unauth_api_client
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
    update_data = {
        'name': 'patch_category'
    }
    # when:
    url = reverse('item-category-detail', args=[categories[0].id])
    response = client.patch(
        url,
        data=json.dumps(update_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 200
    assert response.data['name'] == update_data['name']


@pytest.mark.django_db
def test_patch_item_category_as_user(
    jwt_auth_api_client,
    create_num_of_item_categories_in_array
):
    # given: a superuser and some categories
    categories = create_num_of_item_categories_in_array(5)
    client = jwt_auth_api_client
    update_data = {
        'name': 'patch_category'
    }
    # when:
    url = reverse('item-category-detail', kwargs={'pk': categories[0].id})
    response = client.patch(
        url,
        data=json.dumps(update_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_delete_item_category_as_admin(
    admin_user,
    unauth_api_client,
    create_num_of_item_categories_in_array
):
    # given: a superuser and some categories
    categories = create_num_of_item_categories_in_array(5)
    token = AccessToken.for_user(admin_user)
    client = unauth_api_client
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
    # when:
    url = reverse('item-category-detail', args=[categories[0].id])
    response = client.delete(
        url
    )
    db_cats = ItemCategory.objects.all()
    # then:
    assert response.status_code == 204
    assert response.data is None
    assert len(db_cats) == 4


@pytest.mark.django_db
def test_delete_item_category_as_user(
    jwt_auth_api_client,
    create_num_of_item_categories_in_array
):
    # given: a superuser and some categories
    categories = create_num_of_item_categories_in_array(5)
    client = jwt_auth_api_client
    # when:
    url = reverse('item-category-detail', kwargs={'pk': categories[0].id})
    response = client.patch(
        url
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'
