# ChatPlatform

A platform for chatting with AI agents, using authentication via EVM wallets.

## Features

- 🔐 **Wallet authentication**: Sign-in and registration via EVM wallet signature only
- 💬 **Chat system**: Create and manage chats with AI agents
- 📊 **Rate limiting**: Control usage of AI messages and API calls
- 🚀 **High performance**: Asynchronous architecture on FastAPI
- 🐳 **Docker**: Full containerization for easy deployment
- 🧪 **Testing**: Unit test coverage of core components

## Tech stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Caching**: Redis 7
- **Auth**: JWT + EVM signatures
- **Containerization**: Docker + Docker Compose
- **Testing**: Pytest

## Architecture

The project follows Clean Architecture principles:

```
src/main/
├── domain/          # Data models (SQLAlchemy ORM)
├── services/        # Business logic
├── routers/         # API endpoints
├── persistence/     # Data access (DAO)
├── dto/            # API models (DTOs)
├── clients/        # External services
├── exceptions/     # Custom exceptions
└── utils/          # Utilities
```

## Core entities

### User
- `wallet_address`: EVM wallet address (unique)
- `email`: User email (optional)
- `ai_messages_limit`: Limit for AI messages
- `ai_messages_used`: Used AI messages
- `api_calls_limit`: Limit for API calls
- `api_calls_used`: Used API calls

### Chat
- `title`: Chat title
- `user_id`: Owner user ID
- `message_count`: Number of messages
- `created_at`, `updated_at`: Timestamps

### Message
- `content`: Message content
- `role`: Sender role (USER/AI)
- `chat_id`: Chat ID
- `user_id`: User ID
- `model_used`: AI model used (for AI messages)
- `tokens_used`: Number of tokens (for AI messages)

## API endpoints

### Auth (`/auth`)
- `POST /auth/authenticate` - Authenticate (sign-in or signup) via wallet signature
- `POST /auth/add-email` - Add email to an existing user
- `GET /auth/message` - Get a message for signing

### Users (`/user`)
- `GET /user/profile` - Get profile
- `PUT /user/profile` - Update profile
- `GET /user/limits` - Get limits
- `GET /user/wallet/{address}` - Get user by wallet address

### Chats (`/chat`)
- `POST /chat/` - Create a chat
- `GET /chat/` - Get user's chats
- `GET /chat/recent` - Recent chats
- `GET /chat/{id}` - Get chat by ID
- `PUT /chat/{id}` - Update chat
- `DELETE /chat/{id}` - Delete chat

### Messages (`/message`)
- `POST /message/` - Create a user message
- `GET /message/chat/{id}` - Messages of a chat
- `GET /message/chat/{id}/full` - Chat with messages
- `GET /message/chat/{id}/recent` - Recent messages
- `GET /message/{id}` - Get message by ID
- `PUT /message/{id}` - Update message
- `DELETE /message/{id}` - Delete message

## Setup and run

### 1. Clone the repository
```bash
git clone <repository-url>
cd ChatPlatform/ChatApp
```

### 2. Configure environment
```bash
cp .env .env
# Edit the .env file with your settings
```

### 3. Generate JWT keys
```bash
mkdir -p keys
# Generate RSA keys for JWT
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

### 4. Run with Docker Compose
```bash
docker-compose up -d
```

### 5. Run in development mode
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start the application (choose one):

# Option 1: via run.py (recommended)
python run.py

# Option 2: via start_server.py
python start_server.py

# Option 3: via uvicorn directly
python -m uvicorn src.main.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run a specific test
pytest tests/test_auth_service.py
```

## Configuration

Main environment variables:

```env
# Database
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

# Email (optional)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# App
APP_HOST=0.0.0.0
APP_PORT=8000
APP_WORKERS=1
ENVIRONMENT=development
```

## Rate limits

Each user has limits for:
- **AI messages**: Number of messages the AI agent can send
- **API calls**: Number of external API calls

Limits are checked when:
- Creating AI messages
- Calling external APIs
- Updating the profile

## Security

- **JWT tokens**: RS256 algorithm with private/public keys
- **Signature verification**: Validate EVM signatures for authentication
- **CORS**: Configured for frontend integration
- **Data validation**: Pydantic models for all inputs
- **Error handling**: Global exception handling

## Development

### Project structure
- Follows Clean Architecture principles
- Layered separation: domain, services, routers, persistence
- Uses dependency injection
- Singleton pattern for services

### Adding new features
1. Create a model in `domain/`
2. Add a DTO in `dto/models/`
3. Create a DAO in `persistence/`
4. Implement a service in `services/`
5. Add a router in `routers/`
6. Write tests in `tests/`

## License

MIT License
