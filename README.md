# ChatPlatform

Платформа для чатов с AI агентами, использующая аутентификацию через EVM кошельки.

## Особенности

- 🔐 **Аутентификация через кошелек**: Вход и регистрация только через подпись EVM кошелька
- 💬 **Система чатов**: Создание и управление чатами с AI агентами
- 📊 **Система лимитов**: Контроль использования AI сообщений и API вызовов
- 🚀 **Высокая производительность**: Асинхронная архитектура на FastAPI
- 🐳 **Docker**: Полная контейнеризация для легкого развертывания
- 🧪 **Тестирование**: Покрытие unit-тестами основных компонентов

## Технологический стек

- **Backend**: FastAPI (Python 3.11)
- **База данных**: PostgreSQL 15
- **Кэширование**: Redis 7
- **Аутентификация**: JWT + EVM подписи
- **Контейнеризация**: Docker + Docker Compose
- **Тестирование**: Pytest

## Архитектура

Проект следует принципам Clean Architecture:

```
src/main/
├── domain/          # Модели данных (SQLAlchemy ORM)
├── services/        # Бизнес-логика
├── routers/         # API эндпоинты
├── persistence/     # Доступ к данным (DAO)
├── dto/            # Модели для API
├── clients/        # Внешние сервисы
├── exceptions/     # Пользовательские исключения
└── utils/          # Утилиты
```

## Основные сущности

### User (Пользователь)
- `wallet_address`: EVM адрес кошелька (уникальный)
- `email`: Email пользователя (опционально)
- `ai_messages_limit`: Лимит AI сообщений
- `ai_messages_used`: Использовано AI сообщений
- `api_calls_limit`: Лимит API вызовов
- `api_calls_used`: Использовано API вызовов

### Chat (Чат)
- `title`: Название чата
- `user_id`: ID владельца чата
- `message_count`: Количество сообщений
- `created_at`, `updated_at`: Временные метки

### Message (Сообщение)
- `content`: Содержимое сообщения
- `role`: Роль отправителя (USER/AI)
- `chat_id`: ID чата
- `user_id`: ID пользователя
- `model_used`: Использованная AI модель (для AI сообщений)
- `tokens_used`: Количество токенов (для AI сообщений)

## API Эндпоинты

### Аутентификация (`/auth`)
- `POST /auth/authenticate` - Аутентификация (вход или регистрация) через подпись кошелька
- `POST /auth/add-email` - Добавление email к существующему пользователю
- `GET /auth/message` - Получение сообщения для подписи

### Пользователи (`/user`)
- `GET /user/profile` - Получение профиля
- `PUT /user/profile` - Обновление профиля
- `GET /user/limits` - Получение лимитов
- `GET /user/wallet/{address}` - Получение пользователя по кошельку

### Чаты (`/chat`)
- `POST /chat/` - Создание чата
- `GET /chat/` - Получение чатов пользователя
- `GET /chat/recent` - Недавние чаты
- `GET /chat/{id}` - Получение чата по ID
- `PUT /chat/{id}` - Обновление чата
- `DELETE /chat/{id}` - Удаление чата

### Сообщения (`/message`)
- `POST /message/` - Создание сообщения пользователя
- `GET /message/chat/{id}` - Сообщения чата
- `GET /message/chat/{id}/full` - Чат с сообщениями
- `GET /message/chat/{id}/recent` - Последние сообщения
- `GET /message/{id}` - Получение сообщения по ID
- `PUT /message/{id}` - Обновление сообщения
- `DELETE /message/{id}` - Удаление сообщения

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd ChatPlatform/ChatApp
```

### 2. Настройка окружения
```bash
cp .env .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Генерация JWT ключей
```bash
mkdir -p keys
# Сгенерируйте RSA ключи для JWT
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

### 4. Запуск через Docker Compose
```bash
docker-compose up -d
```

### 5. Запуск в режиме разработки
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения (выберите один из способов):

# Способ 1: Через run.py (рекомендуется)
python run.py

# Способ 2: Через start_server.py
python start_server.py

# Способ 3: Через uvicorn напрямую
python -m uvicorn src.main.main:app --reload --host 0.0.0.0 --port 8000
```

## Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=src

# Запуск конкретного теста
pytest tests/test_auth_service.py
```

## Конфигурация

Основные переменные окружения:

```env
# База данных
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chatplatform
POSTGRES_USER=chatplatform_user
POSTGRES_PASSWORD=chatplatform_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=chatplatform_redis_password

# JWT
JWT_PUBLIC_KEY_PATH=./keys/public.pem
JWT_PRIVATE_KEY_PATH=./keys/private.pem
JWT_ALGORITHM=RS256
JWT_EXPIRE_ACCESS=3600

# Email (опционально)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Приложение
APP_HOST=0.0.0.0
APP_PORT=8000
APP_WORKERS=1
ENVIRONMENT=development
```

## Система лимитов

Каждый пользователь имеет лимиты на:
- **AI сообщения**: Количество сообщений, которые может отправить AI агент
- **API вызовы**: Количество вызовов сторонних API

Лимиты проверяются при:
- Создании AI сообщений
- Вызове внешних API
- Обновлении профиля

## Безопасность

- **JWT токены**: RS256 алгоритм с приватными/публичными ключами
- **Проверка подписей**: Валидация EVM подписей для аутентификации
- **CORS**: Настроен для работы с фронтендом
- **Валидация данных**: Pydantic модели для всех входных данных
- **Обработка ошибок**: Глобальная обработка исключений

## Разработка

### Структура проекта
- Следует принципам Clean Architecture
- Разделение на слои: domain, services, routers, persistence
- Использование dependency injection
- Singleton паттерн для сервисов

### Добавление новых функций
1. Создайте модель в `domain/`
2. Добавьте DTO в `dto/models/`
3. Создайте DAO в `persistence/`
4. Реализуйте сервис в `services/`
5. Добавьте роутер в `routers/`
6. Напишите тесты в `tests/`

## Лицензия

MIT License
