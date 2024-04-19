from factory import LazyAttribute, LazyFunction
from factory.django import DjangoModelFactory, Password
from faker import Faker

from accounts.models import User

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
