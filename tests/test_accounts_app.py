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
    print('post_data:', post_data)
    print('response.data:', response.content.decode('utf-8'))
    # then: expecting to get status code 201 and other passed params
    assert response.status_code == 201
    assert response.data['email'] == post_data['email']
