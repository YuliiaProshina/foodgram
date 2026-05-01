from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscription, Tag,
                            User)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          SubscriptionSerializer, TagSerializer)


class CurrentUserView(APIView):
    """Вьюсет для получения данных о текущем пользователе."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = CustomUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами.
    Обеспечивает создание, просмотр, редактирование
    и удаление рецептов.
    Поддерживает:
    - фильтрацию по автору, тегам, избранному
    и корзине покупок;
    - добавление и удаление рецептов из избранного;
    - добавление и удаление рецептов в корзину покупок;
    - скачивание списка покупок;
    - получение короткой ссылки на рецепт.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author_id=author)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' and user.is_authenticated:
            queryset = queryset.filter(
                favorites__user=user)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.filter(shopping_cart__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=('get',),
        permission_classes=(AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f'/s/{recipe.id}/')
        return Response({'short-link': short_url})

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user,
                                        recipe=recipe)
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart_items = ShoppingCart.objects.filter(user=user,
                                                          recipe=recipe)
        if not shopping_cart_items.exists():
            return Response(
                {'errors': 'Рецепта нет в корзине.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart_items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request, pk=None):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user)
        result = {}
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            unit = ingredient.ingredient.measurement_unit
            if name not in result:
                result[name] = {
                    'amount': 0,
                    'unit': unit,
                }
            result[name]['amount'] += ingredient.amount
        text = 'Список покупок:'
        for name, data in result.items():
            text += f'\n{name}: {data["amount"]} {data["unit"]}'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')
        return response

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=user,
                                             recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            FavoriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe,
                                               context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if not favorite.exists():
            return Response(
                {'errors': 'Рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class AvatarView(APIView):
    """Вьюсет для работы с аваторкой пользователя."""
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': serializer.data['avatar']},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=('avatar',))
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeView(APIView):
    """Вьюсет для работы с подписками."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        if author == request.user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(user=request.user, author=author)
        serializer = SubscriptionSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )
        if not subscription.exists():
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(APIView):
    """Вьюсет для получения списка подписок пользователя.
    Возвращает список авторов, на которых подписан
    текущий авторизованный пользователь.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        authors = User.objects.filter(subscribers__user=request.user)
        paginator = CustomPagination()
        page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
