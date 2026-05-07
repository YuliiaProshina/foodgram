from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from recipes.constants import (MAX_EMAIL_LENGTH, MAX_MEASURE_LENGTH,
                               MAX_NAME_LENGTH, MAX_RECIPE_NAME_LENGTH,
                               MAX_TEXT_LENGTH, MAX_USERNAME_LENGTH)

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Логин может содержать только буквы, цифры и символы @/./+/-/_'
)


class User(AbstractUser):
    """Модель для создания пользователей."""
    email = models.EmailField('Электронная почта',
                              max_length=MAX_EMAIL_LENGTH, unique=True)
    username = models.CharField('Логин', max_length=MAX_USERNAME_LENGTH,
                                unique=True, validators=[username_validator],)
    first_name = models.CharField('Имя', max_length=MAX_USERNAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_USERNAME_LENGTH)
    avatar = models.ImageField('Аватарка', upload_to='users/images/',
                               default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Tag(models.Model):
    """Модель для создания тегов."""
    name = models.CharField('Название тега', max_length=MAX_NAME_LENGTH,
                            unique=True,)
    slug = models.SlugField('Слаг', max_length=MAX_NAME_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для создания ингредиентов."""
    name = models.CharField('Название ингредиента', max_length=MAX_NAME_LENGTH)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=MAX_MEASURE_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для создания рецептов."""
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  blank=True, verbose_name='Теги')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Название рецепта',
                            max_length=MAX_RECIPE_NAME_LENGTH)
    image = models.ImageField('Изображение рецепта',
                              upload_to='recipe/images/', default=None)
    text = models.TextField('Описание рецепта', max_length=MAX_TEXT_LENGTH)
    cooking_time = models.PositiveIntegerField('Время приготовления', default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель для связи рецепта и ингредиента."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты'
    )
    amount = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        unique_together = ('recipe', 'ingredient')


class FavoriteRecipe(models.Model):
    """Модель для добавления рецептов в избранное."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorites'
            )
        ]


class ShoppingCart(models.Model):
    """Модель для создания корзины покупок пользователя."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]


class Subscription(models.Model):
    """Модель для создания подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscriptions'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
