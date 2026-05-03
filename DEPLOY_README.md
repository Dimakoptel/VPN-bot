# 🚀 Быстрое развертывание NexusBot в Docker

Этот скрипт автоматически развертывает VPN-бот со всеми зависимостями в Docker контейнерах.

## 📋 Что включает развертывание

- **NexusBot** — Telegram бот для управления VPN подписками
- **PostgreSQL** — база данных для хранения данных
- **Redis** — кэш для улучшения производительности
- **Автоматическая настройка** — все переменные окружения и конфигурация

## 🛠 Требования

- Docker и Docker Compose
- Минимум 2GB RAM, 5GB дискового пространства

## 🚀 Быстрый запуск

```bash
# Клонируйте репозиторий (если еще не)
git clone https://github.com/Dimakoptel/VPN-bot.git
cd VPN-bot

# Запустите скрипт развертывания
./deploy.sh
```

Скрипт автоматически:
1. ✅ Создаст конфигурационные файлы (`.env`, `docker-compose.yml`)
2. ✅ Сгенерирует случайные пароли для БД и Redis
3. ✅ Соберет и запустит все сервисы
4. ✅ Инициализирует базу данных с таблицами

## 🔧 После развертывания

### 1. Настройте токен бота
Отредактируйте `.env` и замените:
```env
BOT_TOKEN=ваш_реальный_токен_от_BotFather
BOT_ADMIN_IDS=ваш_telegram_id
```

### 2. Перезапустите бота
```bash
docker compose restart bot
```

### 3. Проверьте статус
```bash
docker compose ps
docker compose logs bot
```

## 🌐 Доступ к сервисам

После запуска сервисы доступны на:
- **Бот**: работает в фоне, получает обновления от Telegram
- **PostgreSQL**: `localhost:5432` (пользователь: `nexusbot`)
- **Redis**: `localhost:6379` (с паролем из `.env`)
- **Prometheus метрики**: `localhost:9090/metrics`

## 📊 Управление

```bash
# Просмотр логов
docker compose logs -f bot

# Остановка всех сервисов
docker compose down

# Перезапуск
docker compose restart

# Обновление (после изменений в коде)
docker compose up --build -d
```

## 🔒 Безопасность

- Пароли БД и Redis генерируются автоматически
- Данные сохраняются в `./data/` (не коммитить в git)
- Логи сохраняются в `./logs/`

## 🆘 Решение проблем

### Бот не запускается
- Проверьте токен в `.env`
- Убедитесь, что бот добавлен в Telegram

### Ошибка подключения к БД
```bash
docker compose logs db
docker compose restart db
```

### Очистка и перезапуск
```bash
docker compose down -v  # удалить volumes
rm -rf data/ logs/
./deploy.sh
```

## 📝 Ручная настройка (опционально)

Если скрипт не подходит, настройте вручную:

1. Создайте `.env` на основе `.env.example`
2. Запустите: `docker compose up --build -d`
3. Инициализируйте БД: `python init_db.py` (для локальной разработки)

## 🎯 Следующие шаги

1. Настройте платежную систему (YooKassa, Stripe)
2. Подключите VPN панель (3x-UI)
3. Настройте лицензирование
4. Добавьте домен и SSL для webhook

---

**Примечание**: Для продакшена рассмотрите использование Docker Swarm или Kubernetes для оркестрации.</content>
<parameter name="filePath">/workspaces/VPN-bot/DEPLOY_README.md