import asyncio

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
        if attrs["book"].inventory < 1:
            raise serializers.ValidationError({
                "book": "At the moment, we aren`t having this book."
            })
        return data

    def create(self, validated_data):
        print(validated_data["book"])
        validated_data["book"].inventory -= 1
        validated_data["book"].save()
        asyncio.run(send_message(
            validated_data["borrow_date"],
            validated_data["expected_return_date"],
            validated_data["book"].title,
            "create",
        ))
        return super().create(validated_data)
