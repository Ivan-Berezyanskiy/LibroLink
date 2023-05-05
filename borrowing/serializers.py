import datetime

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from telegram_bot.utils import send_message


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
        send_message.delay(
            validated_data["borrow_date"],
            validated_data["expected_return_date"],
            validated_data["book"].title,
            "create",
        )
        return super().create(validated_data)


class BorrowingReturnSerializer(ModelSerializer):
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

    def validate(self, attrs):
        data = super(BorrowingReturnSerializer, self).validate(attrs)
        if self.instance.actual_return_date:
            raise serializers.ValidationError({
                "actual_return_date": "You can`t twice return this book"
            })
        return data

    def update(self, instance, validated_data):
        instance.actual_return_date = datetime.date.today()
        instance.save()
        instance.book.inventory += 1
        instance.book.save()
        send_message.delay(
            instance.borrow_date,
            instance.expected_return_date,
            instance.book.title,
            "return",
        )
        return instance
