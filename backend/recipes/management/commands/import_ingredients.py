import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Импортирует ингредиенты из CSV-файла."""

    def handle(self, *args, **kwargs):
        with open('./app/data/ingredients.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Ingredient.objects.bulk_create(
                (
                    Ingredient(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                    for row in reader
                ),
                ignore_conflicts=True,
            )
        self.stdout.write(
            self.style.SUCCESS('Ингредиенты импортированы.')
        )
