from django.contrib import admin
from .models import Recipe, Tag, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    inlines = (RecipeIngredientInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Ingredient._meta.fields]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tag._meta.fields]