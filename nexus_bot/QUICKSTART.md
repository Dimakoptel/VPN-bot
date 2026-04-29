# 🚀 Quick Start Guide для NexusBot

## ⚡ Запуск за 2 минуты

### Требование
- Установленный **Docker** и **Docker Compose**

### Шаг 1: Настройка конфигурации

```bash
cd nexus_bot

# Скопируйте шаблон конфигурации
cp .env.example .env
```

### Шаг 2: Отредактируйте `.env`

Откройте файл `.env` и укажите **минимум 2 параметра**:

```ini
# ОБЯЗАТЕЛЬНО - получите токен в @BotFather
BOT_TOKEN=your_real_token_here

# ОБЯЗАТЕЛЬНО - узнайте свой ID в @userinfobot
BOT_ADMIN_IDS=your_telegram_id
```

### Шаг 3: Запустите бота

#### Вариант A: SQLite (быстрый старт, тестирование)
```bash
docker-compose up -d nexusbot
```

#### Вариант B: PostgreSQL + Мониторинг (продакшен)
```bash
# Отредактируйте .env для PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://nexusbot:password@db:5432/nexusbot

docker-compose up -d
```

### Шаг 4: Проверьте работу

```bash
# Просмотр логов
docker-compose logs -f nexusbot

# Проверка статуса
docker-compose ps
```

---

## ✅ Готово!

Бот запущен и готов к работе. Теперь вы можете:

1. **Написать боту** в Telegram
2. **Проверить логи**: `docker-compose logs -f`
3. **Остановить**: `docker-compose down`

---

## 📚 Дальнейшие шаги

- [Полная документация по Docker](DOCKER_DEPLOYMENT.md)
- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [Основной README](README.md)

---

## 🆘 Проблемы?

### Бот не запускается
```bash
# Проверьте логи
docker-compose logs nexusbot

# Убедитесь что токен правильный
docker-compose exec nexusbot env | grep BOT_TOKEN
```

### Нужна помощь
Обратитесь в @nexus_support
