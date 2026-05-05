from recipes.models import RecipeIngredient


def create_shopping_cart_text(user):
    """Формирует текстовый список покупок для пользователя."""
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=user
    ).select_related('ingredient')
    result = {}
    for recipe_ingredient in ingredients:
        name = recipe_ingredient.ingredient.name
        unit = recipe_ingredient.ingredient.measurement_unit
        if name not in result:
            result[name] = {
                'amount': 0,
                'unit': unit,
            }
        result[name]['amount'] += recipe_ingredient.amount
    text = 'Список покупок:'
    for name, data in result.items():
        text += f'\n{name}: {data["amount"]} {data["unit"]}'
    return text
