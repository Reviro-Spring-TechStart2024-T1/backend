import pytest
from faker import Faker
from pytest_factoryboy import register
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import ItemCategoryFactory, UserFactory

register(UserFactory)
register(ItemCategoryFactory)


fake = Faker()


@pytest.fixture
def unauth_api_client():
    return APIClient()


@pytest.fixture
def create_user_from_factory(db) -> UserFactory:
    return UserFactory()


@pytest.fixture
def create_num_of_users_from_factory(db):
    def make_users(num: int) -> list:
        return UserFactory.create_batch(size=num)

    return make_users


@pytest.fixture
def jwt_auth_api_client(create_user_from_factory) -> APIClient:
    """
    Fixture authenticates created user that is created using fixture above.
    Returns authorized APIClient instance.
    """
    user = create_user_from_factory
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    return client


@pytest.fixture
def dict_data_to_create_test_user() -> dict:
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f'{first_name}.{last_name}@drinkjoy.kg'
    password = 'VeryStrongP@$$word123'
    confirm_pass = 'VeryStrongP@$$word123'

    post_data = {
        'email': email,
        'password': password,
        'confirm_password': confirm_pass
    }
    return post_data


@pytest.fixture
def create_num_of_item_categories_in_array(db):
    '''
    Fixture to create number of item categories utilizing factories.
        usage:
            categories = create_num_of_item_categories_in_array(5)
        result:
            ['category1', 'category2', 'category3', 'category4', 'category5']
    '''
    def make_num_of_categories(num: int = 1) -> list:
        return ItemCategoryFactory.create_batch(size=num)
    return make_num_of_categories
