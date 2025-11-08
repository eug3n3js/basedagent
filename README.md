# BasedAgent

A crypto AI copilot platform for on-chain analytics, wallet insights, NFT intelligence, and X-account influence checks. Users can chat with AI agents using EVM wallet authentication.

## 🚀 Features

- 🔐 **Wallet Authentication**: Sign-in and registration via EVM wallet signature only
- 💬 **AI Chat System**: Create and manage conversations with AI agents
- 🔍 **On-Chain Analytics**: Real-time blockchain data analysis
- 🖼️ **NFT Intelligence**: Collection analysis via OpenSea MCP integration
- 🐦 **X/Twitter Analysis**: Account influence checks via TweetScout
- 📧 **Email Verification**: Optional email verification for user accounts
- 🚀 **High Performance**: Asynchronous architecture built on FastAPI
- 🐳 **Docker Support**: Full containerization for easy deployment

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Caching**: Redis 7
- **Authentication**: JWT (RS256) + EVM wallet signatures
- **AI/LLM**: OpenAI GPT models
- **External Services**: 
  - OpenSea MCP (NFT data)
  - TweetScout API (Twitter analytics)
  - GraphQL endpoint (on-chain data)
- **Containerization**: Docker + Docker Compose

## 📐 Architecture

The project follows Clean Architecture principles with clear separation of concerns:

```
src/main/
├── domain/          # Data models (SQLAlchemy ORM)
├── services/        # Business logic layer
├── routers/         # API endpoints (FastAPI routes)
├── persistence/     # Data access layer (DAO pattern)
├── dto/            # API models (DTOs and converters)
├── clients/        # External service clients
│   ├── llm_client.py
│   ├── mcp_client.py
│   ├── indexer_client.py
│   ├── email_client.py
│   └── redis_client.py
├── exceptions/     # Custom exception classes
├── constants/      # Application constants
└── utils/          # Utility functions
```

## 📦 Core Entities

### User
- `wallet_address`: EVM wallet address (unique identifier)
- `email`: User email (optional, unique, can be verified)
- `remaining_chat_credits`: Remaining chat credits balance (float)
- `created_at`: Account creation timestamp
- `chats`: Relationship to user's chats

### Chat
- `title`: Chat title (auto-generated from messages)
- `user_id`: Owner user reference (foreign key)
- `created_at`: Chat creation timestamp
- `messages`: Relationship to chat messages

### Message
- `content`: Message text content
- `role`: Sender role (`USER` or `AI` - MessageRole enum)
- `chat_id`: Parent chat reference (foreign key)
- `created_at`: Message creation timestamp

## 🔌 API Endpoints

### Authentication (`/auth`)
- `GET /auth/message` - Get message for wallet signing
- `POST /auth/authenticate` - Authenticate (sign-in or signup) via wallet signature
- `POST /auth/send-email-code` - Send email verification code
- `POST /auth/verify-email-code` - Verify email code and add email to account

### Users (`/user`)
- `GET /user/me` - Get current user profile
- `GET /user/portfolio` - Get user portfolio data

### Chats (`/chat`)
- `GET /chat/chats` - Get all user's chats (with pagination: `limit`, `offset`)
- `POST /chat/new` - Create a new chat
- `GET /chat/tasks` - Get available task types
- `GET /chat/{chat_id}` - Get chat by ID
- `GET /chat/{chat_id}/status` - Get chat processing status
- `GET /chat/{chat_id}/messages` - Get messages in a chat (with pagination)
- `POST /chat/{chat_id}/message/new` - Send a new message to chat
- `POST /chat/{chat_id}/message/new/{task_name}` - Send a message with specific task type

### Events (`/events`)
- `GET /events/all` - Get all user events (deposit and spend events)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15 (if running without Docker)
- Redis 7 (if running without Docker)
- OpenSSL (for JWT key generation)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd basedagent
```

### 2. Environment Configuration

Create a `.env` file in the root directory with the required environment variables (see [Configuration](#-configuration) section).

### 3. Generate JWT Keys

```bash
# Create keys directory
mkdir -p keys

# Generate RSA private key
openssl genrsa -out keys/private.pem 2048

# Generate RSA public key
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

### 4. Run with Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL, Redis, App)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```


The API will be available at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chatplatform
POSTGRES_USER=chatplatform_user
POSTGRES_PASSWORD=chatplatform_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=chatplatform_redis_password

# JWT Configuration
JWT_PUBLIC_KEY_PATH=./keys/public.pem
JWT_PRIVATE_KEY_PATH=./keys/private.pem
JWT_ALGORITHM=RS256
JWT_EXPIRE_ACCESS=3600

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# OpenSea MCP Configuration
OPENSEA_MCP_URL=your-opensea-mcp-url
OPENSEA_BEARER_TOKEN=your-opensea-bearer-token

# TweetScout Configuration
TWEETSCOUT_API_KEY=your-tweetscout-api-key

# GraphQL/Indexer Configuration
GRAPHQL_ENDPOINT=your-graphql-endpoint

# Email Configuration (Mailtrap)
MAILTRAP_API_TOKEN=your-mailtrap-api-token
EMAIL_FROM_ADDRESS=noreply@basedagent.io
EMAIL_FROM_NAME=BasedAgent

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_WORKERS=1
ENVIRONMENT=development
```

## 💳 Credit System

The platform uses a credit-based system to control resource usage:

- **Chat Credits**: Users have a `remaining_chat_credits` balance (float)
- **Credit Usage**: Credits are deducted when processing messages:
  - Base cost: 0.1 credits per message
  - Additional costs for MCP tool usage (OpenSea, TweetScout, etc.)
- **Credit Sources**: 
  - Credits can be purchased via the blockchain credit system (see `creditsys/`)
  - New users receive 2.0 credits upon registration
- **Credit Enforcement**: Messages cannot be processed if user has insufficient credits (balance <= 0)

## 🔒 Security

- **JWT Authentication**: RS256 algorithm with RSA private/public key pairs
- **EVM Signature Verification**: Cryptographic validation of wallet signatures
- **CORS**: Configurable CORS middleware for frontend integration
- **Input Validation**: Pydantic models for all API inputs
- **Error Handling**: Global exception handler with proper error responses
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## 🏗️ Development

### Project Structure Guidelines

The project follows Clean Architecture principles:

1. **Domain Layer** (`domain/`): Core business entities and models
2. **DTO Layer** (`dto/`): Data transfer objects for API communication
3. **Persistence Layer** (`persistence/`): Data access objects (DAO pattern)
4. **Service Layer** (`services/`): Business logic implementation
5. **Router Layer** (`routers/`): API endpoint definitions
6. **Client Layer** (`clients/`): External service integrations

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for all functions
- Document complex functions with docstrings
- Keep functions focused and single-purpose

## 📚 Additional Resources

- **Credit System**: See `creditsys/README.md` for blockchain credit system documentation


## 📄 License

MIT License

---

**Note**: This project is for informational purposes only and does not provide financial advice.
