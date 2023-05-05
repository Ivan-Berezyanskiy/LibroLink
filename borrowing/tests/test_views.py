from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer
from borrowing.tests.samples import sample_book, sample_borrowing

BOOK_URL = reverse("book:book-list")
BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_url(borrowing_id: int, returned: bool = False):
    if returned:
        return reverse("borrowing:borrowing-return", args=[borrowing_id])
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowing(self):
        sample_borrowing(book=sample_book())
        sample_borrowing(book=sample_book())

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_active(self):
        book = sample_book()

        borrowing1 = sample_borrowing(book=book, actual_return_date="2023-12-12")
        borrowing2 = sample_borrowing(book=book)

        res = self.client.get(BORROWING_URL, {"is_active": True})

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_filter_borrowings_by_user_is_forbidden_for_user_and_user_can_only_see_his_borrowings(self):
        book = sample_book(inventory=3)

        borrowing1 = sample_borrowing(book=book)
        borrowing2 = sample_borrowing(book=book)

        get_user_model().objects.create_user(
            "tesdst@test.com",
            "testpass",
        )
        borrowing3 = sample_borrowing(book=book, user_id=2)
        res = self.client.get(BORROWING_URL, {"user_id": 2})

        serializer1 = BorrowingSerializer(borrowing1)
        serializer2 = BorrowingSerializer(borrowing2)
        serializer3 = BorrowingSerializer(borrowing3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_borrowing_detail(self):
        book = sample_book()
        borrowing = sample_borrowing(book=book)

        url = detail_url(borrowing_id=borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_put_borrowing_not_allowed(self):
        book = sample_book()
        payload1 = {
            "borrow_date": "2002-06-02",
            "expected_return_date": "2022-07-02",
            "user_id": 1,
            "book": book,
        }
        payload2 = {"expected_return_date": "2012-07-02"}
        borrowing = sample_borrowing(book=book)
        url = detail_url(borrowing.id)

        res_put = self.client.put(url, payload1)
        res_patch = self.client.patch(url, payload2)

        self.assertEqual(res_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res_patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_borrowing_not_allowed(self):
        borrowing = sample_borrowing(book=sample_book())
        url = detail_url(borrowing.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
