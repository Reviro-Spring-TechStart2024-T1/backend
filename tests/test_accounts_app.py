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
    print(response.content.decode('utf-8'))
    # then: expecting to get status code 201 and other passed params
    assert response.status_code == 201
    assert response.data['access'] is not None
    assert response.data['refresh'] is not None


@pytest.mark.django_db
def test_get_profile_with_jwt_auth_user(
    jwt_auth_api_client
):
    # given: authenticated user
    client = jwt_auth_api_client(role='customer')
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
    client = jwt_auth_api_client(role='customer')
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
    client = jwt_auth_api_client(role='customer')
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


@pytest.mark.django_db
def test_put_change_password_as_auth_user(
    jwt_auth_api_client
):
    # given: autheticated user
    client = jwt_auth_api_client(role='customer')
    url = reverse('change_password')
    old_pass = 'VeryStrongP@$$123'
    new_pass = 'superVeryStrongP@$$123'
    put_data = {
        'old_password': old_pass,
        'password': new_pass,
        'confirm_password': new_pass
    }
    # when:
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 200
    assert response.data['message'] == 'Password updated successfully'


@pytest.mark.django_db
def test_put_change_password_as_anonym_user(
    unauth_api_client
):
    # given: autheticated user
    client = unauth_api_client
    url = reverse('change_password')
    old_pass = 'VeryStrongP@$$123'
    new_pass = 'superVeryStrongP@$$123'
    put_data = {
        'old_password': old_pass,
        'password': new_pass,
        'confirm_password': new_pass
    }
    # when:
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 401
    assert response.data['detail'] == 'Authentication credentials were not provided.'


@pytest.mark.django_db
def test_creation_of_partner_user(
    create_user_from_factory
):
    partner = create_user_from_factory(role='partner')

    assert partner.role == 'partner'


@pytest.mark.django_db
def test_successful_logout_as_auth_user_with_refresh(
    unauth_api_client
):
    # given: autheticated user
    client = unauth_api_client
    user1 = {
        'email': 'user1@drinkjoy.kg',
        'password': 'user1sReally$trongPass123',
        'confirm_password': 'user1sReally$trongPass123'
    }
    register_url = reverse('register')
    response1 = client.post(
        register_url,
        data=json.dumps(user1),
        content_type='application/json'
    )
    assert response1.status_code == 201
    assert response1.data['access'] is not None
    assert response1.data['refresh'] is not None
    access_token = response1.data['access']
    refresh_token = response1.data['refresh']
    headers = {'Authorization': f'Bearer {access_token}'}
    # when:
    url = reverse('logout')
    response = client.post(
        url,
        headers=headers,
        data=json.dumps({
            'refresh_token': refresh_token
        }),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_unsuccessful_logout_as_auth_user_with_access(
    unauth_api_client
):
    # given: autheticated user
    client = unauth_api_client
    user1 = {
        'email': 'user1@drinkjoy.kg',
        'password': 'user1sReally$trongPass123',
        'confirm_password': 'user1sReally$trongPass123'
    }
    register_url = reverse('register')
    response1 = client.post(
        register_url,
        data=json.dumps(user1),
        content_type='application/json'
    )
    assert response1.status_code == 201
    assert response1.data['access'] is not None
    assert response1.data['refresh'] is not None
    access_token = response1.data['access']
    headers = {'Authorization': f'Bearer {access_token}'}
    # when:
    url = reverse('logout')
    response = client.post(
        url,
        headers=headers,
        data=json.dumps({
            'refresh_token': access_token
        }),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 400
    assert response.data['detail'] == 'Invalid refresh token.'


@pytest.mark.django_db
def test_get_list_of_all_users_by_admin(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('admin')
    # when:
    url = reverse('users_list')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_get_list_of_all_users_by_customer(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('customer')
    # when:
    url = reverse('users_list')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_list_of_all_users_by_partner(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('partner')
    # when:
    url = reverse('users_list')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_empty_list_of_all_partners_by_admin(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('admin')
    # when:
    url = reverse('register_partner')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 0


@pytest.mark.django_db
def test_get_list_of_all_partners_by_customer(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('customer')
    # when:
    url = reverse('register_partner')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_list_of_all_partners_by_partner(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('partner')
    # when:
    url = reverse('register_partner')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You do not have permission to perform this action.'


@pytest.mark.django_db
def test_get_list_of_all_partners_by_admin(
    jwt_auth_api_client,
    create_user_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    partner = create_user_from_factory('partner')
    # when:
    url = reverse('register_partner')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == partner.id
