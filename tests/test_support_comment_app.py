import json

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_get_empty_list_of_all_comments_as_admin(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('admin')
    # when:
    url = reverse('comments')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_get_list_of_all_comments_as_admin(
    jwt_auth_api_user_and_client,
    create_num_of_comments_as_one_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    num_of_comments = 9
    create_num_of_comments_as_one_user_from_factory(user, num_of_comments)
    # when:
    url = reverse('comments')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == num_of_comments


@pytest.mark.django_db
def test_create_comment_as_admin(
    jwt_auth_api_client,
    create_post_from_factory,
    dict_data_to_create_comment
):
    # given:
    client = jwt_auth_api_client('admin')
    post = create_post_from_factory
    data = dict_data_to_create_comment
    data['post'] = post.id
    # when:
    url = reverse('comments')
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['message'] == data['message']
    assert response.data['post'] == data['post']
    assert response.data['author'] is not None


@pytest.mark.django_db
def test_put_others_comment_as_admin(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    comment = create_comment_from_factory
    put_data = {
        'message': 'updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this comment.'


@pytest.mark.django_db
def test_put_admins_comment_as_admin(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    comment = create_comment_as_specific_user_from_factory(user)
    print(comment)
    put_data = {
        'message': 'updated_message',
        # 'post': comment.post.id
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['message'] == put_data['message']
    assert response.data['id'] == comment.id
    assert response.data['author']['id'] == user.id
    assert response.data['author']['first_name'] == user.first_name
    assert response.data['author']['last_name'] == user.last_name
    assert response.data['author']['avatar'] == user.avatar


@pytest.mark.django_db
def test_patch_others_comment_as_admin(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    comment = create_comment_from_factory
    patch_data = {
        'message': 'patially_updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this comment.'


@pytest.mark.django_db
def test_patch_admins_comment_as_admin(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    comment = create_comment_as_specific_user_from_factory(user)
    patch_data = {
        'message': 'partially_updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 200
    assert response.data['message'] == patch_data['message']
    assert response.data['id'] == comment.id
    assert response.data['author']['id'] == user.id
    assert response.data['author']['first_name'] == user.first_name
    assert response.data['author']['last_name'] == user.last_name
    assert response.data['author']['avatar'] == user.avatar


@pytest.mark.django_db
def test_delete_others_comment_as_admin(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    comment = create_comment_from_factory
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to delete this comment.'


@pytest.mark.django_db
def test_delete_admins_comment_as_admin(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    comment = create_comment_as_specific_user_from_factory(user)
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_get_empty_list_of_all_comments_as_customer(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('customer')
    # when:
    url = reverse('comments')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_get_list_of_all_comments_as_customer(
    jwt_auth_api_user_and_client,
    create_num_of_comments_as_one_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    num_of_comments = 9
    create_num_of_comments_as_one_user_from_factory(user, num_of_comments)
    # when:
    url = reverse('comments')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == num_of_comments


@pytest.mark.django_db
def test_create_comment_as_customer(
    jwt_auth_api_client,
    create_post_from_factory,
    dict_data_to_create_comment
):
    # given:
    client = jwt_auth_api_client('customer')
    post = create_post_from_factory
    data = dict_data_to_create_comment
    data['post'] = post.id
    # when:
    url = reverse('comments')
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['message'] == data['message']
    assert response.data['post'] == data['post']
    assert response.data['author'] is not None


@pytest.mark.django_db
def test_put_others_comment_as_customer(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    comment = create_comment_from_factory
    put_data = {
        'message': 'updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this comment.'


@pytest.mark.django_db
def test_put_customers_comment_as_customer(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    comment = create_comment_as_specific_user_from_factory(user)
    print(comment)
    put_data = {
        'message': 'updated_message',
        # 'post': comment.post.id
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['message'] == put_data['message']
    assert response.data['id'] == comment.id
    assert response.data['author']['id'] == user.id
    assert response.data['author']['first_name'] == user.first_name
    assert response.data['author']['last_name'] == user.last_name
    assert response.data['author']['avatar'] == user.avatar


@pytest.mark.django_db
def test_patch_others_comment_as_customer(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    comment = create_comment_from_factory
    patch_data = {
        'message': 'patially_updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this comment.'


@pytest.mark.django_db
def test_patch_customers_comment_as_customer(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    comment = create_comment_as_specific_user_from_factory(user)
    patch_data = {
        'message': 'patially_updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 200
    assert response.data['message'] == patch_data['message']
    assert response.data['id'] == comment.id
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_delete_others_comment_as_customer(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    comment = create_comment_from_factory
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to delete this comment.'


@pytest.mark.django_db
def test_delete_customers_comment_as_customer(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    comment = create_comment_as_specific_user_from_factory(user)
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_get_empty_list_of_all_comments_as_partner(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('partner')
    # when:
    url = reverse('comments')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_get_list_of_all_comments_as_partner(
    jwt_auth_api_user_and_client,
    create_num_of_comments_as_one_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    num_of_comments = 9
    create_num_of_comments_as_one_user_from_factory(user, num_of_comments)
    # when:
    url = reverse('comments')
    response = client.get(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == num_of_comments


@pytest.mark.django_db
def test_create_comment_as_partner(
    jwt_auth_api_client,
    create_post_from_factory,
    dict_data_to_create_comment
):
    # given:
    client = jwt_auth_api_client('partner')
    post = create_post_from_factory
    data = dict_data_to_create_comment
    data['post'] = post.id
    # when:
    url = reverse('comments')
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['message'] == data['message']
    assert response.data['post'] == data['post']
    assert response.data['author'] is not None


@pytest.mark.django_db
def test_put_others_comment_as_partner(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    comment = create_comment_from_factory
    put_data = {
        'message': 'updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this comment.'


@pytest.mark.django_db
def test_put_partners_comment_as_partner(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    comment = create_comment_as_specific_user_from_factory(user)
    print(comment)
    put_data = {
        'message': 'updated_message',
        # 'post': comment.post.id
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['message'] == put_data['message']
    assert response.data['id'] == comment.id
    assert response.data['author']['id'] == user.id
    assert response.data['author']['first_name'] == user.first_name
    assert response.data['author']['last_name'] == user.last_name
    assert response.data['author']['avatar'] == user.avatar


@pytest.mark.django_db
def test_patch_others_comment_as_partner(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    comment = create_comment_from_factory
    patch_data = {
        'message': 'patially_updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this comment.'


@pytest.mark.django_db
def test_patch_partners_comment_as_partner(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    comment = create_comment_as_specific_user_from_factory(user)
    patch_data = {
        'message': 'patially_updated_message'
    }
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 200
    assert response.data['message'] == patch_data['message']
    assert response.data['id'] == comment.id
    assert response.data['author']['id'] == user.id
    assert response.data['author']['first_name'] == user.first_name
    assert response.data['author']['last_name'] == user.last_name
    assert response.data['author']['avatar'] == user.avatar


@pytest.mark.django_db
def test_delete_others_comment_as_partner(
    jwt_auth_api_client,
    create_comment_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    comment = create_comment_from_factory
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to delete this comment.'


@pytest.mark.django_db
def test_delete_partners_comment_as_partner(
    jwt_auth_api_user_and_client,
    create_comment_as_specific_user_from_factory
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    comment = create_comment_as_specific_user_from_factory(user)
    # when:
    url = reverse('comment_details', args=[comment.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data is None
