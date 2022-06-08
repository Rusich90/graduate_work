# Проектная работа: диплом

В корне нужно создать .env файл и скопировать в него данные из .env_example

Для реальной проверки оплаток нужно прописать реальный BILLING_ID, BILLING_TOKEN

Команда для старта приложения:
```
docker-compose up -d
```

Для миграций:
```
docker-compose -f docker-compose.yaml exec -T app alembic upgrade head
```

Swagger доступен по ссылке http://localhost/api/openapi