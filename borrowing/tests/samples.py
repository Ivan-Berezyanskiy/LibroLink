from book.models import Book
from borrowing.models import Borrowing


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Cool Author",
        "cover": "Hard",
        "inventory": 2,
        "daily_fee": 0.12,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    defaults = {
        "borrow_date": "2022-06-02",
        "expected_return_date": "2022-07-02",
        "user_id": 1,
        "book": None,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)
