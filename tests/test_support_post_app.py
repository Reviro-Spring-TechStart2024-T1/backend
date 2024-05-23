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


@pytest.mark.django_db
def test_delete_comment_and_then_not_see_it_in_post_as_admin(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_post_as_specific_user,
    create_comment_as_specific_user_for_specific_post_from_factory,
    create_num_of_comments_for_single_post_from_factory
):
    # given: auth admin with post and comments
    admin = create_user_from_factory('admin')
    customer = create_user_from_factory('customer')
    admins_post = create_post_as_specific_user(admin)
    customers_comment = create_comment_as_specific_user_for_specific_post_from_factory(
        customer, admins_post
    )
    com1, com2 = create_num_of_comments_for_single_post_from_factory(admins_post, 2)
    admin_client = jwt_auth_api_client_pass_user(admin)
    customer_client = jwt_auth_api_client_pass_user(customer)
    total_comments = len([customers_comment, com1, com2])
    # when: checking the len of comments before customer delets it
    post_detail_url = reverse('post_details', args=[admins_post.id])
    post_detail_response = admin_client.get(post_detail_url)
    assert post_detail_response.status_code == 200
    assert len(post_detail_response.data['comments']) == total_comments
    # when: other user deletes comment
    comment_delete_url = reverse('comment_details', args=[customers_comment.id])
    comment_delete_response = customer_client.delete(comment_delete_url)
    assert comment_delete_response.status_code == 204
    assert comment_delete_response.data is None
    # then: expecting to not see deleted comment in post
    post_detail_url2 = reverse('post_details', args=[admins_post.id])
    post_detail_response2 = admin_client.get(post_detail_url2)
    assert post_detail_response2.status_code == 200
    assert len(post_detail_response2.data['comments']) == total_comments - 1
    post_detail_response3 = customer_client.get(post_detail_url2)
    assert customers_comment not in post_detail_response3.data['comments']


@pytest.mark.django_db
def test_delete_comment_and_then_not_see_it_in_post_as_partner(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_post_as_specific_user,
    create_comment_as_specific_user_for_specific_post_from_factory,
    create_num_of_comments_for_single_post_from_factory
):
    # given: auth admin with post and comments
    partner = create_user_from_factory('partner')
    customer = create_user_from_factory('customer')
    partners_post = create_post_as_specific_user(partner)
    customers_comment = create_comment_as_specific_user_for_specific_post_from_factory(
        customer, partners_post
    )
    com1, com2 = create_num_of_comments_for_single_post_from_factory(partners_post, 2)
    admin_client = jwt_auth_api_client_pass_user(partner)
    customer_client = jwt_auth_api_client_pass_user(customer)
    total_comments = len([customers_comment, com1, com2])
    # when: checking the len of comments before customer delets it
    post_detail_url = reverse('post_details', args=[partners_post.id])
    post_detail_response = admin_client.get(post_detail_url)
    assert post_detail_response.status_code == 200
    assert len(post_detail_response.data['comments']) == total_comments
    # when: other user deletes comment
    comment_delete_url = reverse('comment_details', args=[customers_comment.id])
    comment_delete_response = customer_client.delete(comment_delete_url)
    assert comment_delete_response.status_code == 204
    assert comment_delete_response.data is None
    # then: expecting to not see deleted comment in post
    post_detail_url2 = reverse('post_details', args=[partners_post.id])
    post_detail_response2 = admin_client.get(post_detail_url2)
    assert post_detail_response2.status_code == 200
    assert len(post_detail_response2.data['comments']) == total_comments - 1
    post_detail_response3 = customer_client.get(post_detail_url2)
    assert customers_comment not in post_detail_response3.data['comments']


@pytest.mark.django_db
def test_delete_comment_and_then_not_see_it_in_post_as_customer(
    create_user_from_factory,
    jwt_auth_api_client_pass_user,
    create_post_as_specific_user,
    create_comment_as_specific_user_for_specific_post_from_factory,
    create_num_of_comments_for_single_post_from_factory
):
    # given: auth admin with post and comments
    customer = create_user_from_factory('customer')
    customer1 = create_user_from_factory('customer')
    customers_post = create_post_as_specific_user(customer)
    customers1_comment = create_comment_as_specific_user_for_specific_post_from_factory(
        customer1, customers_post
    )
    com1, com2 = create_num_of_comments_for_single_post_from_factory(customers_post, 2)
    customer_client = jwt_auth_api_client_pass_user(customer)
    customer1_client = jwt_auth_api_client_pass_user(customer1)
    total_comments = len([customers1_comment, com1, com2])
    # when: checking the len of comments before customer delets it
    post_detail_url = reverse('post_details', args=[customers_post.id])
    post_detail_response = customer_client.get(post_detail_url)
    assert post_detail_response.status_code == 200
    assert len(post_detail_response.data['comments']) == total_comments
    # when: other user deletes comment
    comment_delete_url = reverse('comment_details', args=[customers1_comment.id])
    comment_delete_response = customer1_client.delete(comment_delete_url)
    assert comment_delete_response.status_code == 204
    assert comment_delete_response.data is None
    # then: expecting to not see deleted comment in post
    post_detail_url2 = reverse('post_details', args=[customers_post.id])
    post_detail_response2 = customer_client.get(post_detail_url2)
    assert post_detail_response2.status_code == 200
    assert len(post_detail_response2.data['comments']) == total_comments - 1
    post_detail_response3 = customer1_client.get(post_detail_url2)
    assert customers1_comment not in post_detail_response3.data['comments']
