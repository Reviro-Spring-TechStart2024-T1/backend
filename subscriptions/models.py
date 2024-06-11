# from datetime import timedelta

# from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils import timezone

# from accounts.models import User

# class SubscriptionPlan(models.Model):
#     DURATION_CHOICES = [
#         (30, '1 Month'),
#         (90, '3 Months'),
#         (365, '1 Year')
#     ]

#     name = models.CharField(max_length=50)
#     description = models.TextField(blank=True)
#     duration = models.PositiveIntegerField(choices=DURATION_CHOICES)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     free_trial_days = models.PositiveIntegerField(default=0)

#     class Meta:
#         verbose_name = 'Subscription Plan'
#         verbose_name_plural = 'Subscription Plans'

#     def __str__(self):
#         return self.name


# class UserSubscription(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
#     start_date = models.DateTimeField(default=timezone.now)
#     end_date = models.DateTimeField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     is_trial = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = 'User Subscription'
#         verbose_name_plural = 'User Subscriptions'

#     def __str__(self):
#         return f'{self.user.email} - {self.plan.name}'

#     def save(self, *args, **kwargs):
#         if not self.end_date:
#             trial_days = self.plan.free_trial_days if self.is_trial else 0
#             self.end_date = self.start_date + timedelta(days=self.plan.duration + trial_days)
#         super().save(*args, **kwargs)

#     def extend_subscription(self, additional_days):
#         self.end_date += timedelta(days=additional_days)
#         self.save()

#     def cancel_subscription(self):
#         self.is_active = False
#         self.save()

#     def remaining_days(self):
#         if self.end_date and self.is_active:
#             return (self.end_date - timezone.now()).days
#         return 0

#     def clean(self):
#         if self.end_date and self.end_date <= self.start_date:
#             raise ValidationError('End date must be after start date.')


# @receiver(post_save, sender=UserSubscription)
# def update_subscription_status(sender, instance, **kwargs):
#     if instance.end_date and instance.end_date <= timezone.now() and instance.is_active:
#         instance.is_active = False
#         instance.save()


class PayPalProduct(models.Model):
    product_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    create_time = models.DateTimeField()
    links = models.JSONField()

    def __str__(self):
        return self.name


class Frequency(models.Model):
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    YEAR = 'YEAR'

    INTERVAL_UNITS = [
        (DAY, 'Day'),
        (WEEK, 'Week'),
        (MONTH, 'Month'),
        (YEAR, 'Year'),
    ]

    interval_unit = models.CharField(max_length=5, choices=INTERVAL_UNITS)
    interval_count = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(365)])


class FixedPrice(models.Model):
    AUD = 'AUD'
    BRL = 'BRL'
    CAD = 'CAD'
    CNY = 'CNY'
    CZK = 'CZK'
    DKK = 'DKK'
    EUR = 'EUR'
    HKD = 'HKD'
    HUF = 'HUF'
    ILS = 'ILS'
    JPY = 'JPY'
    MYR = 'MYR'
    MXN = 'MXN'
    TWD = 'TWD'
    NZD = 'NZD'
    NOK = 'NOK'
    PHP = 'PHP'
    PLN = 'PLN'
    GBP = 'GBP'
    SGD = 'SGD'
    SEK = 'SEK'
    CHF = 'CHF'
    THB = 'THB'
    USD = 'USD'

    CURRENCY_CODES = [
        (AUD, 'Australian dollar'),
        (BRL, 'Brazilian real'),
        (CAD, 'Canadian dollar'),
        (CNY, 'Chinese Renmenbi'),
        (CZK, 'Czech koruna'),
        (DKK, 'Danish krone'),
        (EUR, 'Euro'),
        (HKD, 'Hong Kong dollar'),
        (HUF, 'Hungarian forint'),
        (ILS, 'Israeli new shekel'),
        (JPY, 'Japanese yen'),
        (MYR, 'Malaysian ringgit'),
        (MXN, 'Mexican peso'),
        (TWD, 'New Taiwan dollar'),
        (NZD, 'New Zealand dollar'),
        (NOK, 'Norwegian krone'),
        (PHP, 'Philippine peso'),
        (PLN, 'Polish złoty'),
        (GBP, 'Pound sterling'),
        (SGD, 'Singapore dollar'),
        (SEK, 'Swedish krona'),
        (CHF, 'Swiss franc'),
        (THB, 'Thai baht'),
        (USD, 'United States dollar'),
    ]
    value_regex = RegexValidator(
        regex=r'^(([0-9]+)|([0-9]+[.][0-9]+))$',
        message='As string enter a valid positive integer or decimal number.'
    )
    value = models.CharField(max_length=32, validators=[value_regex])
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CODES, default=USD)


class PricingScheme(models.Model):
    fixed_price = models.OneToOneField(FixedPrice, on_delete=models.CASCADE, related_name='pricing_scheme')


class BillingCycle(models.Model):
    TRIAL = 'TRIAL'
    REGULAR = 'REGULAR'

    TENURE_TYPES = [
        ('TRIAL', 'Trial'),
        ('REGULAR', 'Regular'),
    ]
    frequency = models.OneToOneField(Frequency, on_delete=models.CASCADE, related_name='billing_cycle')
    tenure_type = models.CharField(max_length=7, choices=TENURE_TYPES)
    sequence = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    total_cycles = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(999)])
    pricing_scheme = models.OneToOneField(PricingScheme, on_delete=models.CASCADE,
                                          null=True, blank=True, related_name='billing_cycle')


class PaymentPreferences(models.Model):
    CONTINUE = 'CONTINUE'
    CANCEL = 'CANCEL'

    SETUP_FEE_FAILURE_ACTIONS = [
        (CONTINUE, 'Continue'),
        (CANCEL, 'Cancel'),
    ]
    auto_bill_outstanding = models.BooleanField(default=True)
    setup_fee = models.OneToOneField(FixedPrice, on_delete=models.CASCADE, related_name='payment_preferences')
    setup_fee_failure_action = models.CharField(max_length=8, choices=SETUP_FEE_FAILURE_ACTIONS, default=CANCEL)
    payment_failure_threshold = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(999)])


class Taxes(models.Model):
    percentage_regex = RegexValidator(
        regex=r'^((-?[0-9]+)|(-?([0-9]+)?[.][0-9]+))$',
        message='Please enter a valid number. This can be an integer (e.g. 0, 45) or a floating-point number (e.g. 0.6, 98.5).'
    )
    percentage = models.CharField(validators=[percentage_regex])
    inclusive = models.BooleanField(default=True)


class PayPalSubscriptionPlan(models.Model):
    CREATED = 'CREATED'
    INACTIVE = 'INACTIVE'
    ACTIVE = 'ACTIVE'

    STATUS_CHOICES = [
        (CREATED, 'The plan was created. You cannot create subscriptions for a plan in this state.'),
        (INACTIVE, 'The plan is inactive.'),
        (ACTIVE, 'The plan is active. You can only create subscriptions for a plan in this state.'),
    ]
    plan_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    product_id = models.CharField(max_length=100)
    name = models.CharField(max_length=127)
    description = models.CharField(max_length=127)
    value_regex = RegexValidator(
        regex=r'^(([0-9]+)|([0-9]+[.][0-9]+))$',
        message='As string enter a valid positive integer or decimal number.'
    )
    price = models.CharField(max_length=32, blank=True, null=True, validators=[value_regex])
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=ACTIVE)
    billing_cycles = models.ManyToManyField(BillingCycle, related_name='pay_pal_subscription_plan')
    payment_preferences = models.OneToOneField(
        PaymentPreferences, on_delete=models.CASCADE, related_name='pay_pal_subscription_plan', null=True, blank=True)
    taxes = models.OneToOneField(Taxes, on_delete=models.CASCADE,
                                 related_name='pay_pal_subscription_plan', null=True, blank=True)
    links = models.JSONField(null=True, blank=True)
