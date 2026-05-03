#!/bin/bash

# Скрипт автоматического развертывания NexusBot в Docker
# Запускает полный стек: бот + PostgreSQL + Redis

set -e

echo "🚀 Начинаем автоматическое развертывание NexusBot..."

# Проверяем наличие Docker и Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создаем директорию для данных
echo "📁 Создаем директории для данных..."
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p logs

# Генерируем случайные пароли если не заданы
if [ -z "$POSTGRES_PASSWORD" ]; then
    POSTGRES_PASSWORD=$(openssl rand -base64 12)
    echo "🔑 Сгенерирован пароль для PostgreSQL: $POSTGRES_PASSWORD"
fi

if [ -z "$REDIS_PASSWORD" ]; then
    REDIS_PASSWORD=$(openssl rand -base64 12)
    echo "🔑 Сгенерирован пароль для Redis: $REDIS_PASSWORD"
fi

# Создаем .env файл для бота
echo "📝 Создаем конфигурационный файл..."
cat > .env << EOF
# Bot Configuration
BOT_TOKEN=${BOT_TOKEN:-123456789:AAFakeTokenForTestingPurposes123}
BOT_ADMIN_IDS=${BOT_ADMIN_IDS:-123456789,987654321}

# Database - PostgreSQL
DATABASE_URL=postgresql+asyncpg://nexusbot:${POSTGRES_PASSWORD}@db:5432/nexusbot

# License Server (optional)
LICENSE_SERVER_URL=${LICENSE_SERVER_URL:-}
LICENSE_KEY=${LICENSE_KEY:-}

# Payment Provider
PAYMENT_PROVIDER_TOKEN=${PAYMENT_PROVIDER_TOKEN:-your_payment_token}
PAYMENT_CURRENCY=RUB

# VPN Panel Integration
VPN_PANEL_URL=${VPN_PANEL_URL:-http://localhost:8080}
VPN_PANEL_LOGIN=admin
VPN_PANEL_PASSWORD=secure_password

# App Settings
APP_NAME=NexusBot
APP_VERSION=1.0.0
SUPPORT_USERNAME=@nexus_support

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Monitoring Configuration
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090

# Database secrets
POSTGRES_DB=nexusbot
POSTGRES_USER=nexusbot
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
EOF

# Создаем docker-compose.yml
echo "🐳 Создаем Docker Compose конфигурацию..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: nexusbot_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    networks:
      - nexusbot_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: nexusbot_redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    networks:
      - nexusbot_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # NexusBot Application
  bot:
    build:
      context: ./nexus_bot
      dockerfile: Dockerfile
    container_name: nexusbot_app
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - BOT_ADMIN_IDS=${BOT_ADMIN_IDS}
      - DATABASE_URL=${DATABASE_URL}
      - LICENSE_SERVER_URL=${LICENSE_SERVER_URL}
      - LICENSE_KEY=${LICENSE_KEY}
      - PAYMENT_PROVIDER_TOKEN=${PAYMENT_PROVIDER_TOKEN}
      - PAYMENT_CURRENCY=${PAYMENT_CURRENCY}
      - VPN_PANEL_URL=${VPN_PANEL_URL}
      - VPN_PANEL_LOGIN=${VPN_PANEL_LOGIN}
      - VPN_PANEL_PASSWORD=${VPN_PANEL_PASSWORD}
      - APP_NAME=${APP_NAME}
      - APP_VERSION=${APP_VERSION}
      - SUPPORT_USERNAME=${SUPPORT_USERNAME}
      - REDIS_URL=${REDIS_URL}
      - LOG_LEVEL=${LOG_LEVEL}
      - LOG_FILE=${LOG_FILE}
      - LOG_MAX_BYTES=${LOG_MAX_BYTES}
      - LOG_BACKUP_COUNT=${LOG_BACKUP_COUNT}
      - PROMETHEUS_ENABLED=${PROMETHEUS_ENABLED}
      - PROMETHEUS_PORT=${PROMETHEUS_PORT}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "9090:9090"  # Prometheus metrics
    networks:
      - nexusbot_network
    healthcheck:
      test: ["CMD", "python", "-c", "import asyncio; asyncio.run(__import__('core.database').db_manager.initialize())"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  nexusbot_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

# Создаем init скрипт для PostgreSQL
echo "🗄️ Создаем скрипт инициализации базы данных..."
cat > init-db.sql << 'EOF'
-- Инициализация базы данных NexusBot
-- Этот скрипт выполняется при первом запуске PostgreSQL

-- Создание пользователя если не существует (уже создано через env)
-- GRANT ALL PRIVILEGES ON DATABASE nexusbot TO nexusbot;

-- Настройка расширений если нужно
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Создаем .dockerignore для оптимизации сборки
echo "📦 Создаем .dockerignore..."
cat > .dockerignore << 'EOF'
.git
.gitignore
README.md
.env
data/
logs/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
node_modules/
EOF

# Запускаем сборку и запуск
echo "🏗️ Собираем и запускаем сервисы..."
if command -v docker-compose &> /dev/null; then
    docker-compose up --build -d
else
    docker compose up --build -d
fi

# Ждем запуска сервисов
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверяем статус
echo "🔍 Проверяем статус развертывания..."
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi

# Проверяем логи бота
echo "📋 Логи бота:"
if command -v docker-compose &> /dev/null; then
    docker-compose logs bot | tail -20
else
    docker compose logs bot | tail -20
fi

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "🌐 Сервисы доступны:"
echo "  - Бот: работает в фоне"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Prometheus метрики: localhost:9090"
echo ""
echo "📊 Для просмотра логов: docker-compose logs -f bot"
echo "🛑 Для остановки: docker-compose down"
echo "🔄 Для перезапуска: docker-compose restart"
echo ""
echo "⚠️  Не забудьте заменить BOT_TOKEN на реальный токен от @BotFather!"