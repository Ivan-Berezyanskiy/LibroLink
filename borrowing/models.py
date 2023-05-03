from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="borrowing",
    )

    def save(self, *args, **kwargs) -> None:
        if self.book.inventory < 1:
            raise ValidationError(
                "At the moment, we aren`t having this book."
            )
        self.book.inventory -= 1
        self.book.save()
        super(Borrowing, self).save(*args, **kwargs)
