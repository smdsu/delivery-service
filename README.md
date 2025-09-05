# Delivery Service

Современный микросервис для управления доставкой посылок с асинхронной обработкой и расчетом стоимости доставки.

## 🚀 Основные особенности

### Архитектура
- **FastAPI** - современный веб-фреймворк с автоматической документацией
- **PostgreSQL** - надежная реляционная база данных с поддержкой UUID
- **RabbitMQ** - асинхронная обработка сообщений с retry-механизмом
- **Docker** - контейнеризация для простого развертывания
- **Alembic** - миграции базы данных

### Ключевые возможности
- 📦 **Управление посылками** - создание, просмотр и фильтрация посылок
- 💰 **Автоматический расчет стоимости** - на основе веса, стоимости содержимого и курса USD
- 🔄 **Асинхронная обработка** - расчет стоимости в фоновом режиме через RabbitMQ
- 🌐 **Валютный сервис** - получение актуального курса USD с кэшированием
- 🍪 **Сессионная система** - отслеживание пользователей через cookies
- 🛡️ **Безопасность** - middleware для заголовков безопасности
- 📊 **Мониторинг** - health check endpoint и логирование

### Технические особенности
- **Асинхронность** - полная поддержка async/await
- **Типизация** - строгая типизация с Pydantic и SQLAlchemy 2.0
- **Retry-механизм** - автоматические повторы при ошибках обработки
- **Dead Letter Queue** - обработка неудачных сообщений
- **Connection pooling** - оптимизированные подключения к БД
- **Graceful shutdown** - корректное завершение работы

## 🏗️ Структура проекта

```
delivery-service/
├── src/
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── packages.py     # Управление посылками
│   │       └── package_types.py # Типы посылок
│   ├── core/                   # Конфигурация
│   │   ├── app_settings.py     # Настройки приложения
│   │   ├── db_settings.py      # Настройки БД
│   │   └── mq_settings.py      # Настройки RabbitMQ
│   ├── models/                 # SQLAlchemy модели
│   ├── schemas/                # Pydantic схемы
│   ├── services/               # Бизнес-логика
│   │   ├── packages.py         # Сервис посылок
│   │   ├── currency.py         # Валютный сервис
│   │   ├── rabbitmq_producer.py # Публикация в RabbitMQ
│   │   └── package_worker.py   # Обработка посылок
│   ├── workers/                # Фоновые задачи
│   │   └── package_consumer.py # Consumer RabbitMQ
│   ├── crud/                   # Операции с БД
│   └── migrations/             # Миграции Alembic
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile                  # Основное приложение
├── Dockerfile.worker           # Worker процесс
└── pyproject.toml             # Зависимости Poetry
```

## 🚀 Быстрый старт

### Предварительные требования
- Docker и Docker Compose
- Python 3.10+ (для локальной разработки)
- Poetry (для управления зависимостями)

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd delivery-service
```

### 2. Создание .env файла

Создайте файл `.env` в корне проекта:

```env
# Database settings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_db_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_secure_password

# Application settings
APP_NAME=Delivery Service
APP_VERSION=v0.0.1
APP_DEBUG=true
APP_TIMEZONE=UTC

# Security settings
APP_SECRET_KEY=your_super_secret_key_at_least_32_characters_long
APP_ALGORITHM=HS256
APP_ENCRYPTION_KEY=your_encryption_key_at_least_32_chars_long
APP_ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS settings
APP_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
APP_CORS_ALLOW_CREDENTIALS=true

# API settings
APP_API_V1_PREFIX=/api/v1
APP_DOCS_URL=/docs
APP_REDOC_URL=/redoc

# RabbitMQ
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=your_secure_password_here
RABBITMQ_DEFAULT_VHOST=/
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672

```

### 3. Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 4. Проверка работы

- **API документация**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)

## 📚 API Endpoints

### Посылки

```bash
# Создание посылки
POST /api/v1/packages
{
  "name": "Мой пакет",
  "type_id": 1,
  "weight": 2.5,
  "value_of_contents_usd": 100.00
}

# Получение списка посылок
GET /api/v1/packages?page=1&size=20&type_id=1&has_delivery_cost=true

# Получение посылки по ID
GET /api/v1/packages/{package_id}
```

### Типы посылок

```bash
# Получение всех типов
GET /api/v1/package_types
```

## 🔧 Локальная разработка

### Установка зависимостей

```bash
# Установка Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell
```

### Запуск локально

```bash
# Запуск только инфраструктуры
docker-compose up -d postgres rabbitmq

# Применение миграций
alembic upgrade head

# Запуск API сервера
python -m src.main

# Запуск worker в отдельном терминале
python -m src.workers.package_consumer
```

### Полезные команды

```bash
# Создание новой миграции
alembic revision --autogenerate -m "description"

# Применение миграций
alembic upgrade head

# Откат миграций
alembic downgrade -1

# Линтинг
ruff check src/
black src/

# Тесты
pytest
```

## 🐳 Docker

### Основное приложение (Dockerfile)
- Python 3.10 slim
- Автоматическое применение миграций при запуске
- Оптимизированный образ без dev зависимостей

### Worker процесс (Dockerfile.worker)
- Отдельный контейнер для обработки сообщений
- Масштабируемость через реплики

### Docker Compose сервисы
- **postgres**: PostgreSQL 16 с оптимизированными настройками
- **rabbitmq**: RabbitMQ с Management UI
- **app**: Основное FastAPI приложение
- **packages_worker**: Worker для обработки посылок

## 🔄 Асинхронная обработка

### Поток обработки посылки

1. **Создание посылки** → API сохраняет в БД
2. **Публикация в RabbitMQ** → Сообщение отправляется в очередь
3. **Worker обработка** → Получение курса USD и расчет стоимости
4. **Обновление БД** → Сохранение рассчитанной стоимости

### Особенности RabbitMQ
- **Durable queues** - сообщения сохраняются при перезапуске
- **Dead Letter Queue** - обработка неудачных сообщений
- **Retry mechanism** - автоматические повторы с экспоненциальной задержкой
- **Message TTL** - автоматическое удаление старых сообщений

## 💰 Расчет стоимости доставки

Формула расчета:
```
base_cost_usd = weight * 0.5 + value_of_contents_usd * 0.01
delivery_cost_rub = base_cost_usd * usd_rate
```

Где:
- `weight` - вес посылки в кг
- `value_of_contents_usd` - стоимость содержимого в USD
- `usd_rate` - актуальный курс USD/RUB (кэшируется на 30 минут)

## 🛡️ Безопасность

- **Security Headers** - автоматические заголовки безопасности
- **CORS** - настраиваемая политика CORS
- **Session Management** - безопасные HTTP-only cookies
- **Input Validation** - валидация через Pydantic
- **Error Handling** - централизованная обработка ошибок

## 📊 Мониторинг

### Health Check
```bash
curl http://localhost:8000/health
```

### Логирование
- Структурированные логи с контекстом
- Различные уровни логирования
- Логирование ошибок и критических событий

### RabbitMQ Management
- Веб-интерфейс для мониторинга очередей
- Статистика сообщений и производительности
- Управление соединениями и каналами

## 🔧 Конфигурация

### Настройки производительности

В `docker-compose.yml` настроены лимиты ресурсов:
- **PostgreSQL**: 512MB RAM, 0.5 CPU
- **App**: 512MB RAM, 0.5 CPU
- **Worker**: 256MB RAM, 0.25 CPU

## 🚀 Развертывание в продакшене

### Рекомендации
1. Измените пароли в `.env`
2. Отключите `APP_DEBUG=false`
3. Настройте мониторинг и логирование
4. Используйте внешние сервисы для БД и RabbitMQ
5. Настройте SSL/TLS
6. Используйте reverse proxy (nginx)

### Масштабирование
```bash
# Увеличение количества worker'ов
docker-compose up -d --scale packages_worker=3
```

## 📝 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs`
2. Убедитесь в корректности `.env` файла
3. Проверьте доступность портов
4. Создайте issue в репозитории
