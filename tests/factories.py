from factory import (
    LazyAttribute,
    LazyAttributeSequence,
    LazyFunction,
    SubFactory,
    lazy_attribute,
    post_generation,
)
from factory.django import DjangoModelFactory, Password
from faker import Faker
from faker.providers import BaseProvider

from accounts.models import User
from establishments.models import Establishment
from menu.models import Beverage, Category, Menu


class KyrgyzPhoneNumberProvider(BaseProvider):
    def kg_phone_number(self):
        return '+996-{}-{}'.format(
            self.random_number(digits=3, fix_len=True),
            self.random_number(digits=6, fix_len=True)
        )


fake = Faker()


fake.add_provider(KyrgyzPhoneNumberProvider)


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = LazyFunction(fake.first_name)
    last_name = LazyFunction(fake.last_name)
    password = Password('VeryStrongP@$$123')
    email = LazyAttributeSequence(
        lambda obj, count: '%s@example.com' % (obj.first_name + '.' + obj.last_name + str(count))
    )
    is_superuser = False
    date_of_birth = fake.date()
    is_active = True
    is_staff = False

    @lazy_attribute
    def role(self):
        return 'customer'

    @post_generation
    def admin(self, create, extracted, **kwargs):
        if extracted:
            self.role = 'admin'
            self.is_superuser = True
            self.is_staff = True

    @post_generation
    def partner(self, create, extracted, **kwargs):
        if extracted:
            self.role = 'partner'


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = LazyFunction(fake.word)


class EstablishmentFactory(DjangoModelFactory):
    class Meta:
        model = Establishment

    owner = SubFactory(UserFactory)
    name = LazyFunction(fake.word)
    email = LazyFunction(fake.email)
    latitude = fake.pydecimal(
        left_digits=2,
        right_digits=8,
        positive=True
    )
    longitude = fake.pydecimal(
        left_digits=3,
        right_digits=8,
        positive=True
    )
    description = LazyFunction(fake.word)
    phone_number = LazyFunction(fake.kg_phone_number)
    happy_hour_start = LazyFunction(fake.time)
    happy_hour_end = LazyFunction(fake.time)


class MenuFactory(DjangoModelFactory):
    class Meta:
        model = Menu

    establishment = SubFactory(EstablishmentFactory)


class BeverageFactory(DjangoModelFactory):
    class Meta:
        model = Beverage

    menu = SubFactory(MenuFactory)
    name = LazyFunction(fake.word)
    category = SubFactory(CategoryFactory)
    price = LazyAttribute(lambda _: fake.pydecimal(3, 2, True))
    description = LazyFunction(fake.word)
    in_stock = LazyAttribute(lambda _: fake.pyint(min_value=0, max_value=100))
