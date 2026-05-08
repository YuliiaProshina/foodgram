from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.urls import include, path
from django.contrib.admin.sites import NotRegistered
from rest_framework.authtoken.models import Token, TokenProxy

from recipes.models import Recipe

try:
    admin.site.unregister(Token)
    admin.site.unregister(TokenProxy)
except NotRegistered:
    pass


def redirect_short_link(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect(f'/recipes/{recipe.id}/')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:pk>/', redirect_short_link, name='short-link'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
