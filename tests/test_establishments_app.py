import json

import pytest
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import AccessToken


@pytest.mark.django_db
def test_get_empty_establishments_list_as_partner(
    jwt_auth_api_client
):
    # given: client with role partner
    client = jwt_auth_api_client(role='partner')
    # when:
    url = reverse('establishment-list')
    response = client.get(url)
    # then:
    assert response.status_code == 200


@pytest.mark.django_db
def test_if_factory_creates_establishment_with_owner(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-list')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.json()['results'][0]['id'] == est.id
    assert response.json()['results'][0]['owner'] == est.owner.id
    assert response.json()['results'][0]['name'] == est.name
    assert response.json()['results'][0]['email'] == est.email
    assert response.json()['results'][0]['latitude'] == str(est.latitude)
    assert response.json()['results'][0]['longitude'] == str(est.longitude)
    assert response.json()['results'][0]['description'] == est.description
    assert response.json()['results'][0]['phone_number'] == est.phone_number
    assert response.json()['results'][0]['happy_hour_start'] == est.happy_hour_start
    assert response.json()['results'][0]['happy_hour_end'] == est.happy_hour_end


@pytest.mark.django_db
def test_len_of_num_of_factories_as_auth_user(
    jwt_auth_api_client,
    create_num_of_establishments_from_factory
):
    # given:
    client = jwt_auth_api_client(role='customer')
    establishments = create_num_of_establishments_from_factory(5)
    # when:
    url = reverse('establishment-list')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.json()['results']) == len(establishments)


@pytest.mark.django_db
def test_len_of_num_of_factories_as_unauth_user(
    unauth_api_client,
    create_num_of_establishments_from_factory
):
    # given:
    client = unauth_api_client
    establishments = create_num_of_establishments_from_factory(5)
    # when:
    url = reverse('establishment-list')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.json()['results']) == len(establishments)


@pytest.mark.django_db
def test_establishment_creation_as_customer(
    dict_data_to_create_establishment,
    unauth_api_client,
    create_user_from_factory
):
    # given:
    user = create_user_from_factory(role='customer')
    client = unauth_api_client
    access = AccessToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    est_data = dict_data_to_create_establishment(user=user)
    # when:
    url = reverse('establishment-list')
    response = client.post(
        url,
        data=json.dumps(est_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_establishment_creation_as_partner(
    dict_data_to_create_establishment,
    unauth_api_client,
    create_user_from_factory
):
    # given:
    user = create_user_from_factory(role='partner')
    client = unauth_api_client
    access = AccessToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    est_data = dict_data_to_create_establishment(user=user)
    # when:
    url = reverse('establishment-list')
    response = client.post(
        url,
        data=json.dumps(est_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['owner'] == user.id
    assert response.data['name'] == est_data['name']
    assert response.data['email'] == est_data['email']
    assert response.data['latitude'] == est_data['latitude']
    assert response.data['longitude'] == est_data['longitude']
    assert response.data['description'] == est_data['description']
    assert response.data['phone_number'] == est_data['phone_number']
    assert response.data['happy_hour_start'] == est_data['happy_hour_start']
    assert response.data['happy_hour_end'] == est_data['happy_hour_end']


@pytest.mark.django_db
def test_establishment_creation_as_admin(
    dict_data_to_create_establishment,
    unauth_api_client,
    create_user_from_factory
):
    # given:
    user = create_user_from_factory(role='admin')
    client = unauth_api_client
    access = AccessToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access))
    est_data = dict_data_to_create_establishment(user=user)
    # when:
    url = reverse('establishment-list')
    response = client.post(
        url,
        data=json.dumps(est_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_specific_establishment_as_customer(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='customer')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['id'] == est.id
    assert response.data['owner'] == est.owner.id
    assert response.data['name'] == est.name
    assert response.data['email'] == est.email
    assert response.data['latitude'] == str(est.latitude)
    assert response.data['longitude'] == str(est.longitude)
    assert response.data['description'] == est.description
    assert response.data['phone_number'] == est.phone_number
    assert response.data['logo'] == est.logo
    assert response.data['banner_image'] == est.banner_image
    assert response.data['happy_hour_start'] == est.happy_hour_start
    assert response.data['happy_hour_end'] == est.happy_hour_end


@pytest.mark.django_db
def test_get_specific_establishment_as_partner(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['id'] == est.id
    assert response.data['owner'] == est.owner.id
    assert response.data['name'] == est.name
    assert response.data['email'] == est.email
    assert response.data['latitude'] == str(est.latitude)
    assert response.data['longitude'] == str(est.longitude)
    assert response.data['description'] == est.description
    assert response.data['phone_number'] == est.phone_number
    assert response.data['logo'] == est.logo
    assert response.data['banner_image'] == est.banner_image
    assert response.data['happy_hour_start'] == est.happy_hour_start
    assert response.data['happy_hour_end'] == est.happy_hour_end


@pytest.mark.django_db
def test_get_specific_establishment_as_admin(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='admin')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['id'] == est.id
    assert response.data['owner'] == est.owner.id
    assert response.data['name'] == est.name
    assert response.data['email'] == est.email
    assert response.data['latitude'] == str(est.latitude)
    assert response.data['longitude'] == str(est.longitude)
    assert response.data['description'] == est.description
    assert response.data['phone_number'] == est.phone_number
    assert response.data['logo'] == est.logo
    assert response.data['banner_image'] == est.banner_image
    assert response.data['happy_hour_start'] == est.happy_hour_start
    assert response.data['happy_hour_end'] == est.happy_hour_end


@pytest.mark.django_db
def test_patch_specific_establishment_as_partner(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    est = create_establishment_from_factory
    patch_data = {
        'name': 'patched_name',
        'description': 'patched_description',
        'happy_hour_start': '09:00:00',
        'happy_hour_end': '19:00:00'
    }
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 200
    assert response.data['name'] == patch_data['name']
    assert response.data['description'] == patch_data['description']
    assert response.data['happy_hour_start'] == patch_data['happy_hour_start']
    assert response.data['happy_hour_end'] == patch_data['happy_hour_end']


@pytest.mark.django_db
def test_patch_specific_establishment_as_customer(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='customer')
    est = create_establishment_from_factory
    patch_data = {
        'name': 'patched_name',
        'description': 'patched_description',
        'happy_hour_start': '09:00:00',
        'happy_hour_end': '19:00:00'
    }
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_patch_specific_establishment_as_admin(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='admin')
    est = create_establishment_from_factory
    patch_data = {
        'name': 'patched_name',
        'description': 'patched_description',
        'happy_hour_start': '09:00:00',
        'happy_hour_end': '19:00:00'
    }
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_delete_specific_establishment_as_partner(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='partner')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data == None


@pytest.mark.django_db
def test_delete_specific_establishment_as_customer(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='customer')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_delete_specific_establishment_as_admin(
    jwt_auth_api_client,
    create_establishment_from_factory
):
    # given:
    client = jwt_auth_api_client(role='admin')
    est = create_establishment_from_factory
    # when:
    url = reverse('establishment-detail', args=[est.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'
