import json

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_get_empty_list_of_posts_as_admin(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('admin')
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_get_list_of_one_post_as_admin(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    post = create_post_from_factory
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == post.title
    assert response.data['results'][0]['content'] == post.content
    assert response.data['results'][0]['author']['id'] == post.author.id


@pytest.mark.django_db
def test_get_list_of_many_posts_as_admin(
    jwt_auth_api_client,
    create_num_of_posts_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    num_of_posts = 3
    create_num_of_posts_from_factory(num_of_posts)
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == num_of_posts


@pytest.mark.django_db
def test_get_list_of_one_post_with_comments_as_admin(
    jwt_auth_api_client,
    create_post_from_factory,
    create_num_of_comments_for_single_post_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    post = create_post_from_factory
    num_of_comments = 5
    create_num_of_comments_for_single_post_from_factory(post, num_of_comments)
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == post.title
    assert response.data['results'][0]['content'] == post.content
    assert response.data['results'][0]['author']['id'] == post.author.id
    assert len(response.data['results'][0]['comments']) == num_of_comments


@pytest.mark.django_db
def test_create_post_as_admin(
    jwt_auth_api_client,
    dict_data_to_create_post
):
    # given:
    client = jwt_auth_api_client('admin')
    data = dict_data_to_create_post
    # when:
    url = reverse('posts')
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['title'] == data['title']
    assert response.data['content'] == data['content']
    assert response.data['author'] is not None


@pytest.mark.django_db
def test_put_others_post_as_admin(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    post = create_post_from_factory
    post_author = post.author.id
    print(post_author)
    put_data = {
        'title': 'updated_title',
        'content': 'updated_content'
    }
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this post.'


@pytest.mark.django_db
def test_patch_others_post_as_admin(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    post = create_post_from_factory
    patch_data = {
        'title': 'partially_updated_title',
        'content': 'partially_updated_content'
    }
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this post.'


@pytest.mark.django_db
def test_put_admins_post_as_admin(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    put_data = {
        'title': 'updated_title',
        'content': 'updated_content'
    }
    url = reverse('post_details', args=[post.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['title'] == put_data['title']
    assert response.data['content'] == put_data['content']
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_patch_admins_post_as_admin(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    patch_data = {
        'title': 'partially_updated_title',
        'content': 'partially_updated_content'
    }
    url = reverse('post_details', args=[post.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['title'] == patch_data['title']
    assert response.data['content'] == patch_data['content']
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_delete_others_post_as_admin(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('admin')
    post = create_post_from_factory
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.delete(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to delete this post.'


@pytest.mark.django_db
def test_delete_admins_post_as_admin(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('admin')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_get_empty_list_of_posts_as_customer(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('customer')
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_get_list_of_one_post_as_customer(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    post = create_post_from_factory
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == post.title
    assert response.data['results'][0]['content'] == post.content
    assert response.data['results'][0]['author']['id'] == post.author.id


@pytest.mark.django_db
def test_get_list_of_many_posts_as_customer(
    jwt_auth_api_client,
    create_num_of_posts_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    num_of_posts = 3
    create_num_of_posts_from_factory(num_of_posts)
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == num_of_posts


@pytest.mark.django_db
def test_get_list_of_one_post_with_comments_as_customer(
    jwt_auth_api_client,
    create_post_from_factory,
    create_num_of_comments_for_single_post_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    post = create_post_from_factory
    num_of_comments = 5
    create_num_of_comments_for_single_post_from_factory(post, num_of_comments)
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == post.title
    assert response.data['results'][0]['content'] == post.content
    assert response.data['results'][0]['author']['id'] == post.author.id
    assert len(response.data['results'][0]['comments']) == num_of_comments


@pytest.mark.django_db
def test_create_post_as_customer(
    jwt_auth_api_client,
    dict_data_to_create_post
):
    # given:
    client = jwt_auth_api_client('customer')
    data = dict_data_to_create_post
    # when:
    url = reverse('posts')
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['title'] == data['title']
    assert response.data['content'] == data['content']
    assert response.data['author'] is not None


@pytest.mark.django_db
def test_put_others_post_as_customer(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    post = create_post_from_factory
    post_author = post.author.id
    print(post_author)
    put_data = {
        'title': 'updated_title',
        'content': 'updated_content'
    }
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this post.'


@pytest.mark.django_db
def test_patch_others_post_as_customer(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    post = create_post_from_factory
    patch_data = {
        'title': 'partially_updated_title',
        'content': 'partially_updated_content'
    }
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this post.'


@pytest.mark.django_db
def test_put_customers_post_as_customer(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    put_data = {
        'title': 'updated_title',
        'content': 'updated_content'
    }
    url = reverse('post_details', args=[post.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['title'] == put_data['title']
    assert response.data['content'] == put_data['content']
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_patch_customers_post_as_customer(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    patch_data = {
        'title': 'partially_updated_title',
        'content': 'partially_updated_content'
    }
    url = reverse('post_details', args=[post.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['title'] == patch_data['title']
    assert response.data['content'] == patch_data['content']
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_delete_others_post_as_customer(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('customer')
    post = create_post_from_factory
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.delete(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to delete this post.'


@pytest.mark.django_db
def test_delete_customers_post_as_customer(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('customer')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_get_empty_list_of_posts_as_partner(
    jwt_auth_api_client
):
    # given:
    client = jwt_auth_api_client('partner')
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_get_list_of_one_post_as_partner(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    post = create_post_from_factory
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == post.title
    assert response.data['results'][0]['content'] == post.content
    assert response.data['results'][0]['author']['id'] == post.author.id


@pytest.mark.django_db
def test_get_list_of_many_posts_as_partner(
    jwt_auth_api_client,
    create_num_of_posts_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    num_of_posts = 3
    create_num_of_posts_from_factory(num_of_posts)
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == num_of_posts


@pytest.mark.django_db
def test_get_list_of_one_post_with_comments_as_partner(
    jwt_auth_api_client,
    create_post_from_factory,
    create_num_of_comments_for_single_post_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    post = create_post_from_factory
    num_of_comments = 5
    create_num_of_comments_for_single_post_from_factory(post, num_of_comments)
    # when:
    url = reverse('posts')
    response = client.get(url)
    # then:
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == post.title
    assert response.data['results'][0]['content'] == post.content
    assert response.data['results'][0]['author']['id'] == post.author.id
    assert len(response.data['results'][0]['comments']) == num_of_comments


@pytest.mark.django_db
def test_create_post_as_partner(
    jwt_auth_api_client,
    dict_data_to_create_post
):
    # given:
    client = jwt_auth_api_client('partner')
    data = dict_data_to_create_post
    # when:
    url = reverse('posts')
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    # then:
    assert response.status_code == 201
    assert response.data['title'] == data['title']
    assert response.data['content'] == data['content']
    assert response.data['author'] is not None


@pytest.mark.django_db
def test_put_others_post_as_partner(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    post = create_post_from_factory
    post_author = post.author.id
    print(post_author)
    put_data = {
        'title': 'updated_title',
        'content': 'updated_content'
    }
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this post.'


@pytest.mark.django_db
def test_patch_others_post_as_partner(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    post = create_post_from_factory
    patch_data = {
        'title': 'partially_updated_title',
        'content': 'partially_updated_content'
    }
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to update this post.'


@pytest.mark.django_db
def test_put_partners_post_as_partner(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    put_data = {
        'title': 'updated_title',
        'content': 'updated_content'
    }
    url = reverse('post_details', args=[post.id])
    response = client.put(
        url,
        data=json.dumps(put_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['title'] == put_data['title']
    assert response.data['content'] == put_data['content']
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_patch_partners_post_as_partner(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    patch_data = {
        'title': 'partially_updated_title',
        'content': 'partially_updated_content'
    }
    url = reverse('post_details', args=[post.id])
    response = client.patch(
        url,
        data=json.dumps(patch_data),
        content_type='application/json'
    )
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 200
    assert response.data['title'] == patch_data['title']
    assert response.data['content'] == patch_data['content']
    assert response.data['author']['id'] == user.id


@pytest.mark.django_db
def test_delete_others_post_as_partner(
    jwt_auth_api_client,
    create_post_from_factory
):
    # given:
    client = jwt_auth_api_client('partner')
    post = create_post_from_factory
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.delete(url)
    print(response.content.decode('utf-8'))
    # then:
    assert response.status_code == 403
    assert response.data['detail'] == 'You are not allowed to delete this post.'


@pytest.mark.django_db
def test_delete_partners_post_as_partner(
    jwt_auth_api_user_and_client,
    create_num_of_posts_as_specific_user
):
    # given:
    user, client = jwt_auth_api_user_and_client('partner')
    post = create_num_of_posts_as_specific_user(user, 1)[0]
    # when:
    url = reverse('post_details', args=[post.id])
    response = client.delete(url)
    # then:
    assert response.status_code == 204
    assert response.data is None
