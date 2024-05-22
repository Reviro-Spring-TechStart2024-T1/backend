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


@pytest.mark.django_db
def test_patch_partners_block_as_admin(
    create_user_from_factory,
    jwt_auth_api_client_pass_user
):
    # given: auth admin user blocking a partner by their email
    admin = create_user_from_factory('admin')
    partner = create_user_from_factory('partner')
    admin_client = jwt_auth_api_client_pass_user(admin)
    email = partner.email
    patch_data = {
        'email': email
    }
    # when: admin is passing partners email to patch endpoint
    url = reverse('block-partner')
    response = admin_client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.data)
    # then: expecting to showcase all info on partner and its is_blocked status
    assert response.status_code == 200
    assert response.data['email'] == email
    assert response.data['is_blocked'] is True


@pytest.mark.django_db
def test_patch_partners_unblock_as_admin(
    create_user_from_factory,
    jwt_auth_api_client_pass_user
):
    # given: auth admin user unblocking a partner by their email
    admin = create_user_from_factory('admin')
    partner = create_user_from_factory('partner')
    partner.is_blocked = True
    partner.save()
    admin_client = jwt_auth_api_client_pass_user(admin)
    email = partner.email
    patch_data = {
        'email': email
    }
    # when: admin is passing partners email to patch endpoint
    url = reverse('unblock-partner')
    response = admin_client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.data)
    # then: expecting to showcase all info on partner and its is_blocked status
    assert response.status_code == 200
    assert response.data['email'] == email
    assert response.data['is_blocked'] is False


@pytest.mark.django_db
def test_get_responses_of_blocked_partners_as_admin(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth admin who blocks partner
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(3)
    partner = dict_data['partner']
    establishment = dict_data['establishment']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    admin = create_user_from_factory('admin')
    client = jwt_auth_api_client_pass_user(admin)
    block_url = reverse('block-partner')
    block_response = client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: checking if blocked partners establishment, menu and beverages are not found in other urls
    establishment_detail_url = reverse('establishment-detail', args=[establishment.id])
    menu_detail_url = reverse('menu-detail', args=[menu.id])
    beverage1_detail_url = reverse('beverage-detail', args=[beverages[0].id])
    beverage2_detail_url = reverse('beverage-detail', args=[beverages[1].id])
    beverage3_detail_url = reverse('beverage-detail', args=[beverages[2].id])
    establishment_detail_response = client.get(establishment_detail_url)
    menu_detail_response = client.get(menu_detail_url)
    beverage1_detail_response = client.get(beverage1_detail_url)
    beverage2_detail_response = client.get(beverage2_detail_url)
    beverage3_detail_response = client.get(beverage3_detail_url)
    # then: expecting to get on all related urls 404
    assert establishment_detail_response.status_code == 404
    assert establishment_detail_response.data['detail'] == 'No Establishment matches the given query.'
    assert menu_detail_response.status_code == 404
    assert menu_detail_response.data['detail'] == 'No Menu matches the given query.'
    assert beverage1_detail_response.status_code == 404
    assert beverage1_detail_response.data['detail'] == 'No Beverage matches the given query.'
    assert beverage2_detail_response.status_code == 404
    assert beverage2_detail_response.data['detail'] == 'No Beverage matches the given query.'
    assert beverage3_detail_response.status_code == 404
    assert beverage3_detail_response.data['detail'] == 'No Beverage matches the given query.'


@pytest.mark.django_db
def test_get_responses_of_blocked_partners_as_partner(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth admin who blocks partner and "auth" partner
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(3)
    partner = dict_data['partner']
    establishment = dict_data['establishment']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    admin = create_user_from_factory('admin')
    admin_client = jwt_auth_api_client_pass_user(admin)
    partner_client = jwt_auth_api_client_pass_user(partner)
    block_url = reverse('block-partner')
    block_response = admin_client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: checking if blocked partners establishment, menu and beverages are not found in other urls
    establishment_detail_url = reverse('establishment-detail', args=[establishment.id])
    menu_detail_url = reverse('menu-detail', args=[menu.id])
    beverage1_detail_url = reverse('beverage-detail', args=[beverages[0].id])
    beverage2_detail_url = reverse('beverage-detail', args=[beverages[1].id])
    beverage3_detail_url = reverse('beverage-detail', args=[beverages[2].id])
    establishment_detail_response = partner_client.get(establishment_detail_url)
    menu_detail_response = partner_client.get(menu_detail_url)
    beverage1_detail_response = partner_client.get(beverage1_detail_url)
    beverage2_detail_response = partner_client.get(beverage2_detail_url)
    beverage3_detail_response = partner_client.get(beverage3_detail_url)
    # then: expecting to get on all related urls 404
    assert establishment_detail_response.status_code == 404
    assert establishment_detail_response.data['detail'] == 'No Establishment matches the given query.'
    assert menu_detail_response.status_code == 404
    assert menu_detail_response.data['detail'] == 'No Menu matches the given query.'
    assert beverage1_detail_response.status_code == 404
    assert beverage1_detail_response.data['detail'] == 'No Beverage matches the given query.'
    assert beverage2_detail_response.status_code == 404
    assert beverage2_detail_response.data['detail'] == 'No Beverage matches the given query.'
    assert beverage3_detail_response.status_code == 404
    assert beverage3_detail_response.data['detail'] == 'No Beverage matches the given query.'


@pytest.mark.django_db
def test_get_responses_of_blocked_partners_as_customer(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth admin who blocks partner and auth customer
    dict_data = create_partner_establishment_menu_and_num_of_beverages_as_dict(3)
    partner = dict_data['partner']
    establishment = dict_data['establishment']
    menu = dict_data['menu']
    beverages = dict_data['beverages']
    admin = create_user_from_factory('admin')
    customer = create_user_from_factory('customer')
    admin_client = jwt_auth_api_client_pass_user(admin)
    customer_client = jwt_auth_api_client_pass_user(customer)
    block_url = reverse('block-partner')
    block_response = admin_client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: checking if blocked partners establishment, menu and beverages are not found in other urls
    establishment_detail_url = reverse('establishment-detail', args=[establishment.id])
    menu_detail_url = reverse('menu-detail', args=[menu.id])
    beverage1_detail_url = reverse('beverage-detail', args=[beverages[0].id])
    beverage2_detail_url = reverse('beverage-detail', args=[beverages[1].id])
    beverage3_detail_url = reverse('beverage-detail', args=[beverages[2].id])
    establishment_detail_response = customer_client.get(establishment_detail_url)
    menu_detail_response = customer_client.get(menu_detail_url)
    beverage1_detail_response = customer_client.get(beverage1_detail_url)
    beverage2_detail_response = customer_client.get(beverage2_detail_url)
    beverage3_detail_response = customer_client.get(beverage3_detail_url)
    # then: expecting to get on all related urls 404
    assert establishment_detail_response.status_code == 404
    assert establishment_detail_response.data['detail'] == 'No Establishment matches the given query.'
    assert menu_detail_response.status_code == 404
    assert menu_detail_response.data['detail'] == 'No Menu matches the given query.'
    assert beverage1_detail_response.status_code == 404
    assert beverage1_detail_response.data['detail'] == 'No Beverage matches the given query.'
    assert beverage2_detail_response.status_code == 404
    assert beverage2_detail_response.data['detail'] == 'No Beverage matches the given query.'
    assert beverage3_detail_response.status_code == 404
    assert beverage3_detail_response.data['detail'] == 'No Beverage matches the given query.'


@pytest.mark.django_db
def test_get_responses_for_absence_in_lists_of_blocked_partners_as_admin(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth admin blocks one partner out of num_of_partners
    bevs_in_dict = 3
    num_of_partners = 4
    num_of_bevs = num_of_partners * bevs_in_dict
    partners_dicts = [
        create_partner_establishment_menu_and_num_of_beverages_as_dict(bevs_in_dict)
        for _ in range(num_of_partners)
    ]
    last_dict_data = partners_dicts[-1]
    partner = last_dict_data['partner']
    beverages = last_dict_data['beverages']
    admin = create_user_from_factory('admin')
    client = jwt_auth_api_client_pass_user(admin)
    block_url = reverse('block-partner')
    block_response = client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: admin tries to access the related entites' list endpoints
    establishments_list_url = reverse('establishment-list')
    menus_list_url = reverse('menu-list')
    beverages_list_url = reverse('beverage-list')
    establishments_list_response = client.get(establishments_list_url)
    menus_list_response = client.get(menus_list_url)
    beverages_list_response = client.get(beverages_list_url)
    # then: expects to get the length of results being not num_of_partners but less by one
    assert establishments_list_response.status_code == 200
    assert len(establishments_list_response.data['results']) == num_of_partners - 1
    assert menus_list_response.status_code == 200
    assert len(menus_list_response.data['results']) == 0
    assert beverages_list_response.status_code == 200
    assert len(beverages_list_response.data['results']) == num_of_bevs - len(beverages)


@pytest.mark.django_db
def test_get_responses_for_absence_in_lists_of_blocked_partners_as_partner(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth admin blocks one partner out of num_of_partners and "auth" partner
    bevs_in_dict = 3
    num_of_partners = 4
    num_of_bevs = num_of_partners * bevs_in_dict
    partners_dicts = [
        create_partner_establishment_menu_and_num_of_beverages_as_dict(bevs_in_dict)
        for _ in range(num_of_partners)
    ]
    last_dict_data = partners_dicts[-1]
    partner = last_dict_data['partner']
    beverages = last_dict_data['beverages']
    admin = create_user_from_factory('admin')
    admin_client = jwt_auth_api_client_pass_user(admin)
    partner_client = jwt_auth_api_client_pass_user(partner)
    block_url = reverse('block-partner')
    block_response = admin_client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: admin tries to access the related entites' list endpoints
    establishments_list_url = reverse('establishment-list')
    menus_list_url = reverse('menu-list')
    beverages_list_url = reverse('beverage-list')
    establishments_list_response = partner_client.get(establishments_list_url)
    menus_list_response = partner_client.get(menus_list_url)
    beverages_list_response = partner_client.get(beverages_list_url)
    # then: expects to get the length of results being not num_of_partners but less by one
    assert establishments_list_response.status_code == 200
    assert len(establishments_list_response.data['results']) == num_of_partners - 1
    assert menus_list_response.status_code == 200
    assert len(menus_list_response.data['results']) == 0
    assert beverages_list_response.status_code == 200
    assert len(beverages_list_response.data['results']) == num_of_bevs - len(beverages)


@pytest.mark.django_db
def test_get_responses_for_absence_in_lists_of_blocked_partners_as_customer(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_partner_establishment_menu_and_num_of_beverages_as_dict
):
    # given: auth admin blocks one partner out of num_of_partners and "auth" partner
    bevs_in_dict = 3
    num_of_partners = 4
    num_of_bevs = num_of_partners * bevs_in_dict
    partners_dicts = [
        create_partner_establishment_menu_and_num_of_beverages_as_dict(bevs_in_dict)
        for _ in range(num_of_partners)
    ]
    last_dict_data = partners_dicts[-1]
    partner = last_dict_data['partner']
    beverages = last_dict_data['beverages']
    admin = create_user_from_factory('admin')
    customer = create_user_from_factory('customer')
    admin_client = jwt_auth_api_client_pass_user(admin)
    customer_client = jwt_auth_api_client_pass_user(customer)
    block_url = reverse('block-partner')
    block_response = admin_client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: admin tries to access the related entites' list endpoints
    establishments_list_url = reverse('establishment-list')
    menus_list_url = reverse('menu-list')
    beverages_list_url = reverse('beverage-list')
    establishments_list_response = customer_client.get(establishments_list_url)
    menus_list_response = customer_client.get(menus_list_url)
    beverages_list_response = customer_client.get(beverages_list_url)
    # then: expects to get the length of results being not num_of_partners but less by one
    assert establishments_list_response.status_code == 200
    assert len(establishments_list_response.data['results']) == num_of_partners - 1
    assert menus_list_response.status_code == 200
    assert len(menus_list_response.data['results']) == 0
    assert beverages_list_response.status_code == 200
    assert len(beverages_list_response.data['results']) == num_of_bevs - len(beverages)


@pytest.mark.django_db
def test_post_token_api_for_blocked_partner(
    create_user_from_factory,
    jwt_auth_api_client_pass_user
):
    # given: auth admin blocks partner
    admin = create_user_from_factory('admin')
    partner = create_user_from_factory('partner')
    admin_client = jwt_auth_api_client_pass_user(admin)
    partner_client = jwt_auth_api_client_pass_user(partner)
    block_url = reverse('block-partner')
    block_response = admin_client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    # when: blocked partner is trying to login
    login_url = reverse('token_obtain_pair')
    login_response = partner_client.post(
        login_url,
        data=json.dumps(
            {
                'email': partner.email,
                'password': 'VeryStrongP@$$123'
            }
        ),
        content_type='application/json'
    )
    print(login_response.data)
    # then: expects to see message of their account being blocked
    assert login_response.status_code == 403
    assert login_response.data['detail'] == ('Your account is blocked, please '
                                             'refer to the administrator for further assistance.')


@pytest.mark.django_db
def test_post_token_api_for_unblocked_partner(
    create_user_from_factory,
    jwt_auth_api_client_pass_user
):
    # given: auth admin blocks partner and then unblocks
    admin = create_user_from_factory('admin')
    partner = create_user_from_factory('partner')
    admin_client = jwt_auth_api_client_pass_user(admin)
    partner_client = jwt_auth_api_client_pass_user(partner)
    block_url = reverse('block-partner')
    block_response = admin_client.patch(
        block_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert block_response.data['is_blocked'] is True
    unblock_url = reverse('unblock-partner')
    unblock_response = admin_client.patch(
        unblock_url,
        data=json.dumps({'email': partner.email}),
        content_type='application/json'
    )
    assert unblock_response.data['is_blocked'] is False
    # when: blocked partner is trying to login
    login_url = reverse('token_obtain_pair')
    login_response = partner_client.post(
        login_url,
        data=json.dumps(
            {
                'email': partner.email,
                'password': 'VeryStrongP@$$123'
            }
        ),
        content_type='application/json'
    )
    print(login_response.data)
    # then: expects to be able to get into their account
    assert login_response.status_code == 200
    assert login_response.data['access'] is not None
    assert login_response.data['refresh'] is not None
