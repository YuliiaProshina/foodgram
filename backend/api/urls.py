from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AvatarView, CurrentUserView, IngredientViewSet,
                    RecipeViewSet, SubscribeView, SubscriptionsView,
                    TagViewSet)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/me/avatar/', AvatarView.as_view(), name='user-avatar'),
    path('users/subscriptions/', SubscriptionsView.as_view(),
         name='subscriptions'),
    path('users/<int:pk>/subscribe/', SubscribeView.as_view(),
         name='subscribe'),

    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
