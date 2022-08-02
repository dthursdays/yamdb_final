from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from reviews.models import Category, Genre, Review, Title

from .permissions import IsAdminOrReadOnly, PermissionsOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewUpdateSerializer,
                          TitleCreateSerialize,
                          TitleSerializer, ReviewSerializer)
from .filters import TitleFilter


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleCreateSerialize
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (PermissionsOrReadOnly, )

    def get_rating(self, title):
        score_sum = 0
        reviews_queryset = title.reviews.all()
        for review in reviews_queryset:
            score_sum += review.score
        reviews_count = len(reviews_queryset)
        title.rating = score_sum // reviews_count
        title.save()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)
        self.get_rating(title)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.select_related()

    def perform_destroy(self, instance):
        if (
            instance.author == self.request.user
            or self.request.user.is_moderator
            or self.request.user.is_admin
        ):
            super().perform_destroy(instance)
        else:
            raise PermissionDenied('Удаление чужого контента запрещено!')

    def perform_update(self, serializer):
        if (
            serializer.instance.author == self.request.user
            or self.request.user.is_moderator
            or self.request.user.is_admin
        ):
            title_id = self.kwargs.get('title_id')
            title = get_object_or_404(Title, id=title_id)
            serializer.save(author=self.request.user, title=title)
            self.get_rating(title)
            super().perform_update(serializer)
        else:
            raise PermissionDenied('Изменение чужого контента запрещено!')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewUpdateSerializer
        return ReviewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (PermissionsOrReadOnly, )

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.select_related()
