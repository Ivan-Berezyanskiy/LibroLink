from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from borrowing.tests.samples import sample_book, sample_borrowing


class BorrowingModelTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )

    def test_save(self):
        book0 = sample_book(inventory=0)
        try:
            sample_borrowing(book=book0)
        except ValidationError as e:
            self.assertEqual(e.args,
                             ("At the moment, we aren`t having this book.",))
        book1 = sample_book(inventory=1)
        sample_borrowing(book=book1)
        self.assertEqual(book1.inventory, 0)
