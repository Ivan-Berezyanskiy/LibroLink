from rest_framework.serializers import ModelSerializer

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(ModelSerializer):
    book = BookSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "user",
        )
        read_only_fields = ("id", "user")

    def create(self, validated_data):
        if validated_data["book"].inventory > 0:
            validated_data["book"].inventory -= 1
            validated_data["book"].save()
            return super().create(validated_data)
        return self.errors
