from rest_framework.pagination import PageNumberPagination

from config.settings import settings


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация для API."""
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'limit'
