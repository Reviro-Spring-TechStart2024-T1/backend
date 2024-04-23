from factory import LazyAttribute, LazyFunction, lazy_attribute, post_generation
from factory.django import DjangoModelFactory, Password
from faker import Faker

from accounts.models import User
from establishments.models import Establishment
from menu.models import ItemCategory

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = LazyFunction(fake.first_name)
    last_name = LazyFunction(fake.last_name)
    password = Password('VeryStrongP@$$123')
    email = LazyAttribute(lambda obj: '%s@example.com' % obj.first_name)
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


class ItemCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ItemCategory

    name = LazyFunction(fake.word)


class EstablishmentFactory(DjangoModelFactory):
    class Meta:
        model = Establishment

# owner
# name
# email
# latitude
# longitude
# description
# phone_number
# logo
# banner_image
# happy_hour_start
# happy_hour_end
