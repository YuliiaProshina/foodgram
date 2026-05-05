import base64
from collections import Counter

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from backend.recipes.models import ShoppingCart
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Subscription,
                            Tag, User)


class Base64ImageField(serializers.ImageField):
    """Cериализатор для обработки изображений, переданных в формате Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки и обновления аватара пользователя."""
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации нового пользователя."""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class UserWithSubscriptionSerializer(UserSerializer):
    """Сериализатор пользователя с дополнительной информацией
    о подписке и аватаре."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user,
                                           author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов, связанных с рецептом."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для чтения рецептов.
    Используется при отображении рецептов в API.
    Возвращает полную информацию о рецепте, включая автора,
    теги, ингредиенты и дополнительные вычисляемые поля."""
    author = UserWithSubscriptionSerializer(read_only=True)
    image = Base64ImageField(required=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredients',
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'image',
            'text',
            'cooking_time',
            'name',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'image',
            'text',
            'cooking_time',
            'name',
            'ingredients',
        )

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create((
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )
            for item in ingredients
        ))

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, ingredients)
        instance.save()
        return instance

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        tags = attrs.get('tags')
        cooking_time = attrs.get('cooking_time')
        if not ingredients:
            raise serializers.ValidationError('Нужно указать'
                                              ' хотя бы один ингредиент.')
        if not tags:
            raise serializers.ValidationError('Нужно указать '
                                              'хотя бы один тег.')
        if cooking_time is None or cooking_time <= 0:
            raise serializers.ValidationError('Время приготовления'
                                              ' должно быть больше нуля.')
        ingredient_ids = []
        for item in ingredients:
            ingredient = item['ingredient']
            amount = item['amount']
            if amount <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля.'
                )
            if ingredient.id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            ingredient_ids.append(ingredient.id)
        tag_ids = [tag.id for tag in tags]
        counter = Counter(tag_ids)
        duplicates = [tag_id for tag_id, count in counter.items() if count > 1]
        if duplicates:
            raise serializers.ValidationError(
                f'Теги не должны повторяться. Дубликаты: {duplicates}'
            )
        return attrs

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецепта.
    Используется для отображения минимальной информации о рецепте,
    например, в списках избранного или подписок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписок пользователя.
    Используется для получения информации о пользователях,
    на которых подписан текущий пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'first_name',
            'last_name',
            'username',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен.'
            )
        ]

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context=self.context
        ).data
