from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название тега')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название ингридиента', max_length=100)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name

class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True, verbose_name='Теги')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор рецепта')
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    name = models.CharField('Название рецепта', max_length=256)
    image = models.ImageField('Изображение рецепта', upload_to='recipe/images/', null=True, default=None)
    text = models.TextField('Описание рецепта', max_length=1000)
    cooking_time = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


