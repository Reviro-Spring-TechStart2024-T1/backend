import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from PIL import Image
from pytest_factoryboy import register
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from menu.models import Menu
from support.models import Post
from tests.factories import (
    BeverageFactory,
    CategoryFactory,
    CommentFactory,
    EstablishmentBannerFactory,
    EstablishmentFactory,
    KyrgyzPhoneNumberProvider,
    MenuFactory,
    OrderFactory,
    PostFactory,
    UserFactory,
)

register(UserFactory)
register(CategoryFactory)
register(EstablishmentFactory)
register(MenuFactory)
register(BeverageFactory)
register(EstablishmentBannerFactory)
register(OrderFactory)
register(PostFactory)
register(CommentFactory)


fake = Faker()
fake.add_provider(KyrgyzPhoneNumberProvider)


@pytest.fixture
def unauth_api_client():
    return APIClient()


@pytest.fixture
def create_user_from_factory(db) -> UserFactory:
    def make_user(role='customer', **kwargs):
        if role == 'admin':
            return UserFactory.create(admin=True, **kwargs)
        elif role == 'partner':
            return UserFactory.create(partner=True, **kwargs)
        else:
            return UserFactory.create(**kwargs)
    return make_user


@pytest.fixture
def create_num_of_users_from_factory(db):
    def make_users(num: int) -> list:
        return UserFactory.create_batch(size=num)

    return make_users


@pytest.fixture
def jwt_auth_api_client(
    create_user_from_factory
) -> APIClient:
    """
    Fixture authenticates created user that is created using fixture above.
    Returns authorized APIClient instance.
    """
    def make_role_user(role: str = 'customer'):
        user = create_user_from_factory(role=role)
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        return client
    return make_role_user


@pytest.fixture
def jwt_auth_api_client_and_user(
    create_user_from_factory
) -> APIClient:
    """
    Fixture authenticates created user that is created using fixture above.
    Returns authorized APIClient and User instance as tuple.
    """
    def make_role_user(role: str = 'customer'):
        user = create_user_from_factory(role=role)
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        return user, client
    return make_role_user


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
def create_category_from_factory(db):
    return CategoryFactory()


@pytest.fixture
def create_num_of_categories_in_array(db):
    '''
    Fixture to create number of item categories utilizing factories.
        usage:
            categories = create_num_of_item_categories_in_array(5)
        result:
            ['category1', 'category2', 'category3', 'category4', 'category5']
    '''
    def make_num_of_categories(num: int = 1) -> list:
        return CategoryFactory.create_batch(size=num)
    return make_num_of_categories


@pytest.fixture
def create_establishment_from_factory(db):
    return EstablishmentFactory()


@pytest.fixture
def create_num_of_establishments_from_factory(db):
    def make_num_establishments(num: int = 1) -> list:
        return EstablishmentFactory.create_batch(size=num)
    return make_num_establishments


@pytest.fixture
def dict_data_to_create_establishment() -> dict:
    def wrapper_to_provide_user(user: User):
        data = {
            'owner': user.id,
            'name': fake.word(),
            'email': fake.email(),
            'latitude': str(fake.pydecimal(2, 8, True)),
            'longitude': str(fake.pydecimal(3, 8, True)),
            'description': fake.word(),
            'phone_number': fake.kg_phone_number(),
            'happy_hour_start': fake.time(),
            'happy_hour_end': fake.time(),
        }
        return data
    return wrapper_to_provide_user


@pytest.fixture
def create_establishment_banner_from_factory(db):
    return EstablishmentBannerFactory()


@pytest.fixture
def sample_image_file():
    '''
    Generate an in-memory image for testing uploads.
    '''
    # Create an image using PIL
    image = Image.new('RGB', (100, 100), color='red')
    image_file = io.BytesIO()
    image.save(image_file, format='JPEG')
    image_file.seek(0)

    # Create a SimpleUploadedFile that simulates an uploaded file
    file = SimpleUploadedFile('test.jpg', image_file.read(), content_type='image/jpeg')
    return file


@pytest.fixture
def create_menu_from_factory(db):
    return MenuFactory()


@pytest.fixture
def create_num_of_menus_from_factory(db):
    def make_num_of_menus(num: int = 1) -> list:
        return MenuFactory.create_batch(size=num)
    return make_num_of_menus


@pytest.fixture
def create_beverage_from_factory(db):
    return BeverageFactory()


@pytest.fixture
def create_num_of_beverages_from_factory(db):
    def make_num_of_beverages(num: int = 1) -> list:
        return BeverageFactory.create_batch(size=num)
    return make_num_of_beverages


@pytest.fixture
def create_num_of_beverages_in_one_menu_from_factories(db, create_menu_from_factory):
    def make_num_beverages(num: int = 1) -> list:
        menu = create_menu_from_factory
        items = BeverageFactory.create_batch(size=num, menu=menu)
        return items
    return make_num_beverages


@pytest.fixture
def create_num_of_beverages_in_one_menu_from_outside_factory(db):
    def make_num_of_beverages(menu: Menu, num: int = 1) -> list:
        return BeverageFactory.create_batch(size=num, menu=menu)
    return make_num_of_beverages


@pytest.fixture
def create_order_from_factory(db):
    return OrderFactory()


@pytest.fixture
def create_num_of_orders_for_one_user_from_factory(db):
    def make_num_of_orders(user: User, num: int = 1) -> list:
        return OrderFactory.create_batch(user=user, size=num)
    return make_num_of_orders


def create_post_from_factory(db):
    return PostFactory()


@pytest.fixture
def create_num_of_posts_from_factory(db):
    def make_posts(num: int = 1) -> list:
        return PostFactory.create_batch(size=num)
    return make_posts


@pytest.fixture
def create_comment_from_factory(db):
    return CommentFactory()


@pytest.fixture
def create_num_of_comments_from_factory(db):
    def make_comments(num: int = 1) -> list:
        return CommentFactory.create_batch(size=num)
    return make_comments


@pytest.fixture
def create_num_of_comments_for_single_post_from_factory(db):
    def make_comments(post: Post, num: int = 1) -> list:
        return CommentFactory.create_batch(post=post, size=num)
    return make_comments


@pytest.fixture
def dict_data_to_create_post() -> dict:
    data = {
        'title': fake.word(),
        'content': fake.word(),
        'author': None,
    }
    return data
