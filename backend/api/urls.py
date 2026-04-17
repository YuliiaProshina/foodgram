from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, IngredientViewSet, TagViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),

]
