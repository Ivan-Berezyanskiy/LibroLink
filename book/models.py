from django.contrib.auth import get_user_model
from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    class CoverChoice(models.TextChoices):
        SOFT = "Soft"
        HARD = "Hard"

    cover = models.CharField(
        max_length=4,
        choices=CoverChoice.choices,
        default=CoverChoice.HARD,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models
