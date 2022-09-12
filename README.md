![](https://github.com/dthursdays/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# yamdb_final
Это API проекта yamdb, позволяющего хранить отзывы пользователей на различные произведения

## Как запустить:

Клонировать репозиторий и перейти в директорию с файлами для развертки инфраструктуры в командной строке:
```
git clone https://github.com/dthursdays/yamdb_final.git
```
```
cd yamdb_final/infra
```

Создать и заполнить файл .env по шаблону:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```

Запустить docker-compose:
```
docker-compose up -d
```

Далее необходимо применить миграции и подгрузить статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```

Подгрузить данные из фикстур в базу:
```
docker-compose exec web python manage.py shell
# выполнить в открывшемся терминале:
>>> from django.contrib.contenttypes.models import ContentType
>>> ContentType.objects.all().delete()
>>> quit()

# копируем файл с фикстурами в контейнер и загружаем данные:
docker-compose cp fixtures.json web:/app
docker-compose exec web python manage.py loaddata fixtures.json
```

Можно создать суперпользователя для работы через админку:
```
docker-compose exec web python manage.py createsuperuser
```

Чтобы создать резервную копию базы:
```
docker-compose exec web python manage.py dumpdata > fixtures.json
```

## Список доступных команд:
Подробное описание всех эндпоинтов можно найти по адресу http://127.0.0.1:8000/redoc/ после запуска проекта на локальном сервере

## Технологии:

- python 3.9.7
- django 2.2.16
- django rest framework 3.12.4
- django-filter 21.1
- pyJWT 2.1.0
- gunicorn 20.0.4
- nginx 1.21.3-alpine
- postgresql 14.4-alpine
- Docker Engine 20.10.17
