from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from telegram_bot.bot_logic import send_message


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

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)
        if str(
                attrs["expected_return_date"] - attrs["borrow_date"]
        )[0] in ("-", "0"):
            raise serializers.ValidationError({
                "borrow_date": "You can create borrowing minimum on 1 day"
            })
        return data

    def validate_book(self, value):
        if value.inventory < 1:
            raise serializers.ValidationError({
                "book": "At the moment, we aren`t having this book."
            })
        return value

    def create(self, validated_data):
        validated_data["book"].inventory -= 1
        validated_data["book"].save()
        send_message.delay(
            validated_data["borrow_date"],
            validated_data["expected_return_date"],
            validated_data["book"].title,
            "create",
        )
        return super().create(validated_data)
