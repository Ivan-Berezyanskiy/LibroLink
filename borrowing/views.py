import asyncio
import datetime

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
)
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer, )
from telegram_bot.bot_logic import send_message


class BorrowingViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("user", "book")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("user", "book")
        is_active = self.request.query_params.get("is_active")
        if is_active:
            is_active = True if is_active == "True" else False
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        if not self.request.user.is_superuser:
            return queryset.filter(user=self.request.user)

        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=int(user_id))

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        description="Return book, set actual_return_date today"
    )
    @transaction.atomic
    @action(detail=True, methods=["POST"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if not borrowing.actual_return_date:
            borrowing.actual_return_date = datetime.date.today()
            borrowing.save()
            borrowing.book.inventory += 1
            borrowing.book.save()
            serializer = BorrowingSerializer(borrowing, many=False)
            asyncio.run(send_message(
                serializer.data["borrow_date"],
                serializer.data["expected_return_date"],
                serializer.data["book"]["title"],
                "return",
            ))
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            "You can`t twice return this book",
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        description="Admin can see all borrowings, "
                    "but user can see only his",
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by is_active "
                            "borrowings(returned book or not)",
                examples=[
                    OpenApiExample(
                        "Without is_active",
                        value="",
                    ),
                    OpenApiExample(
                        "Book didn`t return",
                        value="True",
                    ),
                    OpenApiExample(
                        "Book returned",
                        value="False",
                    ),
                ],
            ),
            OpenApiParameter(
                name="user_id",
                type={"type": "list", "item": "number"},
                description="Filter by user_id(only for admins)",
                examples=[
                    OpenApiExample(
                        "Without user_id",
                        value="",
                    ),
                    OpenApiExample(
                        "With user_id",
                        value="1",
                    ),
                    OpenApiExample(
                        "With another user_id",
                        description="logic(2 or 4)",
                        value="2",
                    ),
                ],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
