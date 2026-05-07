import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """Импортирует теги из CSV-файла."""

    def handle(self, *args, **kwargs):
        with open('/app/data/tags.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            Tag.objects.bulk_create(
                (
                    Tag(
                        name=row[0],
                        slug=row[1]
                    )
                    for row in reader
                ),
                ignore_conflicts=True,
            )
        self.stdout.write(
            self.style.SUCCESS('Теги импортированы.')
        )