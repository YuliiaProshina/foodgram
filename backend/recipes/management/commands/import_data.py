import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Импортирует ингредиенты и теги из CSV-файлов."""

    def import_ingredients(self):
        with open('/app/data/ingredients.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            Ingredient.objects.bulk_create(
                (
                    Ingredient(**row)
                    for row in reader
                ),
                ignore_conflicts=True,
            )

    def import_tags(self):
        with open('/app/data/tags.csv', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            Tag.objects.bulk_create(
                (
                    Ingredient(**row)
                    for row in reader
                ),
                ignore_conflicts=True,
            )

    def handle(self, *args, **kwargs):
        self.import_ingredients()
        self.import_tags()
        self.stdout.write(
            self.style.SUCCESS('Ингредиенты и теги импортированы.')
        )
