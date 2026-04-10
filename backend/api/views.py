from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from recipes.models import Recipe, Ingredient, Tag
from rest_framework import mixins, permissions, viewsets

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    #permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          #IsAuthorOrReadOnly)
    #pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
