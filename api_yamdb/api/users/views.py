from random import choice
from string import ascii_lowercase

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import User

from ..permissions import IsUserAdmin
from .serializers import SignUpSerializer, UserAdmSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    if request.method == 'POST':
        email = request.data.get('email')
        code = ''.join(choice(ascii_lowercase) for i in range(12))
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            send_mail('Ваш код подтверждения для API yamdb',
                      f'Ваш код подтверждения: {code}',
                      'yamdb@yamdb.com',
                      [f'{email}'])
            serializer.save(confirmation_code=code)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_gettoken(request):
    if 'username' not in request.data:
        return Response('Неверные данные', status=status.HTTP_400_BAD_REQUEST)
    username = request.data.get('username')
    user = get_object_or_404(User, username=username)
    if request.data.get('confirmation_code') == user.confirmation_code:
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), },
                        status=status.HTTP_200_OK)
    return Response('Неверные данные',
                    status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdmSerializer
    lookup_field = 'username'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        username = self.kwargs.get('username')
        if self.action == 'destroy':
            if username != 'me':
                return (IsUserAdmin(),)
        if self.action == 'retrieve' or 'update':
            if username == 'me':
                return super().get_permissions()
        return (IsUserAdmin(),)

    def get_serializer_class(self):
        username = self.kwargs.get('username')
        if self.action == 'retrieve' or 'partial_update':
            if username == 'me':
                return UserSerializer
        return UserAdmSerializer

    def get_object(self):
        username = self.kwargs.get('username')
        if username == 'me':
            return get_object_or_404(User,
                                     username=self.request.user.username)
        return super().get_object()

    def destroy(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        if username == 'me' or username == request.user.username:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance = get_object_or_404(User, username=username)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
