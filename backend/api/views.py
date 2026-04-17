from django.contrib.auth.password_validation import validate_password
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .permissions import IsAuthorOrReadOnly
from .serializers import RecipeReadSerializer, TagSerializer, IngredientSerializer, RecipeWriteSerializer, \
    CustomUserSerializer, AvatarSerializer, CustomUserCreateSerializer
from recipes.models import Recipe, Ingredient, Tag
from rest_framework import mixins, permissions, viewsets, status

from recipes.models import User


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all().order_by('id')
    authentication_classes = (TokenAuthentication,)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        serializer = CustomUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']},
                status=status.HTTP_200_OK
            )

        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=('avatar',))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
        url_path='set_password'
    )
    def set_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        errors = {}
        if not current_password:
            errors['current_password'] = ['Обязательное поле.']
        if not new_password:
            errors['new_password'] = ['Обязательное поле.']
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if not user.check_password(current_password):
            return Response(
                {'current_password': ['Неверный пароль.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user=user)
        except Exception as error:
            messages = getattr(error, 'messages', [str(error)])
            return Response(
                {'new_password': messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)


class AvatarView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        avatar = request.data.get('avatar')
        if not avatar:
            return Response(
                {'avatar': ['Обязательное поле.']},
                status=400
            )

        serializer = CustomUserSerializer(
            request.user,
            data={'avatar': avatar},
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'avatar': serializer.data['avatar']},
            status=200
        )

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(status=204)
