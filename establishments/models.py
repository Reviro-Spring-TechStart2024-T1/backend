from django.db import models
from accounts.models import User
# from menu.models import Category
from django.core.validators import RegexValidator


class Category(models.Model):
    name = models.CharField(max_length=255)
    establishments = models.ManyToManyField(
        'Establishment',
        related_name='categories',
        through='EstablishmentCategory'
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Establishment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'partner'})
    name = models.CharField(max_length=255)
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    description = models.TextField(blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+996-[0-9]{3}-[0-9]{6}$',
        message="Phone number must be entered in the format: '+996-XXX-XXXXXX'."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=15)   # Later for validation we'll use Regex, we don't know the area code...
    avatar = models.ImageField(upload_to='avatar/', null=True, blank=True)

    class Meta:
        verbose_name = "Establishment"
        verbose_name_plural = "Establishments"

    def __str__(self):
        return self.name


class EstablishmentCategory(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('establishment', 'category')
        verbose_name_plural = "Establishment Categories"

    def __str__(self):
        return f"{self.category.name} at {self.establishment.name}"


class QrCode(models.Model):
    establishment = models.OneToOneField(Establishment, on_delete=models.CASCADE)
    qr_code_image = models.ImageField(upload_to='qrcodes/')

    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"

    def __str__(self):
        return f"QR CODE of the {self.establishment}"

