from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
from establishments.models import Establishment
from accounts.models import User


class Feedback(models.Model):
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'establishment'],
                name='unique_feedback'
            )
        ]

    def __str__(self):
        return f'{self.user.name} - {self.establishment.name} - {self.rating}'

    def clean(self):
        if self.user.role != 'customer':
            raise ValidationError('Only customer users can leave feedback.')
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
