from django.urls import include, path
from rest_framework import routers

from . import views
from .users.views import UsersViewSet, api_gettoken, api_signup

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', UsersViewSet)
router_v1.register('categories', views.CategoryViewSet, basename='categories')
router_v1.register('genres', views.GenreViewSet, basename='genres')
router_v1.register('titles', views.TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>.+)/reviews',
    views.ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
    views.CommentViewSet, basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', api_signup),
    path('v1/auth/token/', api_gettoken),
    path('v1/', include(router_v1.urls)),
]
