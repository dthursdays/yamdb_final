from django.urls import include, path
from rest_framework import routers

from .users.views import UsersViewSet, api_gettoken, api_signup
from .views import (CategoryViewSet, CommentViewSet,
                    GenreViewSet, TitleViewSet, ReviewViewSet)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', UsersViewSet)
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>.+)/reviews',
    ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_gettoken),
    path('v1/', include(router_v1.urls)),
]
