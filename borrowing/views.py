import datetime

from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer, )


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
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            "You can`t twice return this book",
            status=status.HTTP_400_BAD_REQUEST
        )
