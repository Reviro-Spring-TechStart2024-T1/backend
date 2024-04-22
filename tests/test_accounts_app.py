import json

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_register_api_with_unauth_client(
    dict_data_to_create_test_user,
    unauth_api_client
):
    # given: dict_data with user creadentials and unauth api client
    post_data = dict_data_to_create_test_user
    client = unauth_api_client
    # when: executing POST method on register endpoint
    url = reverse('register')
    response = client.post(
        url,
        data=json.dumps(post_data),
        content_type='application/json'
    )
    # then: expecting to get status code 201 and other passed params
    assert response.status_code == 201
    assert response.data['email'] == post_data['email']


@pytest.mark.django_db
def test_get_profile_with_jwt_auth_user(
    jwt_auth_api_client
):
    # given: authenticated user
    client = jwt_auth_api_client
    # when: user is executing GET operation on profile page
    url = reverse('profile')
    response = client.get(
        url
    )
    # then: expecting to get all fields except avatar to be not null
    assert response.status_code == 200
    assert response.data['email'] is not None
    assert response.data['first_name'] is not None
    assert response.data['last_name'] is not None
    assert response.data['sex'] is not None
    assert response.data['date_of_birth'] is not None
    assert response.data['avatar'] is None


@pytest.mark.django_db
def test_put_profile_with_jwt_auth_user(
    jwt_auth_api_client
):
    # given: authenticated user
    client = jwt_auth_api_client
    put_data = {
        'email': 'put_email@drinkjoy.kg',
        'first_name': 'put_first_name',
        'last_name': 'put_last_name',
        'sex': 'male',
        'date_of_birth': '1999-01-01'
    }
    # when: user is willing to change most of the fields except avatar
    url = reverse('profile')
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then: expecting to get correct results
    assert response.status_code == 200
    assert response.data['email'] == put_data['email']
    assert response.data['first_name'] == put_data['first_name']
    assert response.data['last_name'] == put_data['last_name']
    assert response.data['sex'] == put_data['sex']
    assert response.data['date_of_birth'] == put_data['date_of_birth']
    assert response.data['avatar'] is None


@pytest.mark.django_db
def test_email_unique_constraint_works_correctly_with_put_profile_endpoint(
    unauth_api_client
):
    # prerequisite: two users have to be made
    user1 = {
        'email': 'user1@drinkjoy.kg',
        'password': 'user1sReally$trongPass123',
        'confirm_password': 'user1sReally$trongPass123'
    }
    user2 = {
        'email': 'user2@drinkjoy.kg',
        'password': 'user2sReally$trongPass123',
        'confirm_password': 'user2sReally$trongPass123'
    }
    client = unauth_api_client
    register_url = reverse('register')
    response1 = client.post(
        register_url,
        data=json.dumps(user1),
        content_type='application/json'
    )
    assert response1.status_code == 201
    response2 = client.post(
        register_url,
        data=json.dumps(user2),
        content_type='application/json'
    )
    assert response2.status_code == 201
    # given: two users user1 and user2 in database prerequisites above
    login_url = reverse('token_obtain_pair')
    user2_login = {
        'email': 'user2@drinkjoy.kg',
        'password': 'user2sReally$trongPass123'
    }
    response3 = client.post(
        login_url,
        data=json.dumps(user2_login),
        content_type='application/json'
    )
    print(response3.content.decode('utf-8'))
    assert response3.status_code == 200
    access_token = response3.data['access']
    # when: user2 wants to see their credentials and update email to the user1's that is in db
    profile_url = reverse('profile')
    headers = {'Authorization': f'Bearer {access_token}'}
    response4 = client.get(profile_url, headers=headers)
    assert response4.status_code == 200
    assert response4.data['email'] == user2['email']
    put_data = {
        'email': 'user1@drinkjoy.kg'
    }
    response5 = client.put(
        profile_url,
        data=json.dumps(put_data),
        content_type='application/json',
        headers=headers
    )
    # then:
    assert response5.status_code == 400
    assert response5.data['email'] == ['user with this email already exists.']


@pytest.mark.django_db
def test_patch_profile_with_jwt_auth_user(
    jwt_auth_api_client
):
    # given: authenticated user
    client = jwt_auth_api_client
    patch_data = {
        'email': 'patch_email@drinkjoy.kg',
        'first_name': 'patch_first_name',
        'last_name': 'patch_last_name'
    }
    # when: user is willing to change some of the fields
    url = reverse('profile')
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then: expecting to get correct results
    assert response.status_code == 200
    assert response.data['email'] == patch_data['email']
    assert response.data['first_name'] == patch_data['first_name']
    assert response.data['last_name'] == patch_data['last_name']
    assert response.data['sex'] == 'not_say'
    assert response.data['date_of_birth'] is not None
    assert response.data['avatar'] is None
