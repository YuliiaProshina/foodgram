### Описание проекта:

Проект FOODGRAM представляет собой веб-приложение, где пользователи могут публиковать рецепты, добавлять их в избранное, формировать список покупок и подписываться на авторов.

### Технологии проекта:

Django, Python, Django REST Framework, Djoser, Redoc, Nginx, Gunicorn, PostgreSQL, GitHub Actions (CI/CD), Docker, Docker Compose

### Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```python
git clone https://github.com/YuliiaProshina/foodgram.git
```

```python
cd backend
```

Cоздать и активировать виртуальное окружение:

```python
python3 -m venv env
```

* Если у вас Linux/macOS

    ```python
    source env/bin/activate
    ```

* Если у вас windows

    ```python
    source env/scripts/activate
    ```

```python
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```python
pip install -r requirements.txt
```

Выполнить миграции:

```python
python3 manage.py migrate
```

Запустить проект:

```python
python3 manage.py runserver
```
### Как запустить проект через Docker:

```python
cd foodgram
```
```python
docker compose up --build
```
Приложение будет доступно:

* http://localhost:7000
* http://localhost:7000/admin

### Доступные эндпоинты:

**Рецепты**

* GET    /api/recipes/<br>
* POST   /api/recipes/<br>
* GET    /api/recipes/{id}/<br>
* PUT    /api/recipes/{id}/<br>
* PATCH  /api/recipes/{id}/<br>
* DELETE /api/recipes/{id}/<br>

**Теги**

* GET /api/tags/<br>

**Ингредиенты**

* GET /api/ingredients/<br>

**Скачивание списка покупок**

* GET /api/recipes/download_shopping_cart/<br>

## Примеры использования

***Создание рецепта***

Эндпоинт: POST   /api/recipes/<br>

Тело запроса:
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Успешный ответ, код 201:
```python
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "AC+Ej5mo1NcZ16lbXQIsF6yN1AtExlk76ceShBFTFaQVvyg1CH_O70dk.cWFY3xLWLx_6Ysz",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
Негативный ответ при отсутствии обязательного поля, код 400:
```python
{
  "field_name": [
    "Обязательное поле."
  ]
}
```
***Авторизация***

Эндпоинт: POST api/users/

Тело запроса:
```
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
```
Успешный ответ, код 200:
```
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов"
}
```

Негативный ответ при отсутствии обязательного поля, код 400:
```python
{
  "field_name": [
    "Обязательное поле."
  ]
}
```

## Импорт ингредиентов и тегов

Проект поддерживает импорт ингредиентов и тегов из CSV-файлов через Django management commands.

### Структура файлов

Файлы должны находиться в папке:

```text
data/
|--ingredients.csv
|--tags.csv
```

## Формат ingredients.csv

```text
name,measurement_unit
Молоко,мл
Соль,г
Мука,г
```

## Формат tags.csv

```text
name,slug
Завтрак,breakfast
Обед,lunch
Ужин,dinner
```

## Импорт ингредиентов и тегов
## Локально

```python
python manage.py import_data
```

## В Docker

```python
docker compose exec backend python manage.py import_data
```

## На сервере

```python
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_data
```

## Автор
Прошина Юлия - студент Яндекс.Практикума
