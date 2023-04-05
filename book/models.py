from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    class CoverChoice(models.TextChoices):
        SOFT = "Soft"
        HARD = "Hard"

    cover = models.CharField(
        max_length=4,
        choices=CoverChoice.choices,
        default=CoverChoice.HARD,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=(MinValueValidator(limit_value=0.01),),)
