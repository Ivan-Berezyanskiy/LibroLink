from rest_framework import viewsets

from book.models import Book
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().select_related("author")
    serializer_class = BookSerializer
