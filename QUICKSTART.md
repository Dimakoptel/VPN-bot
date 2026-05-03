# 🚀 Быстрый старт с NexusBot

Добро пожаловать! Это руководство поможет вам запустить NexusBot за 5 минут.

## ⚡ Быстрый запуск (Docker)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Dimakoptel/VPN-bot.git
cd VPN-bot

# 2. Запустить развертывание
./deploy.sh

# 3. Готово! Бот работает в фоне
```

## 🔧 Что происходит автоматически

Скрипт `deploy.sh` выполняет:
- ✅ Устанавливает Docker образы (PostgreSQL, Redis, Bot)
- ✅ Создает базу данных с таблицами
- ✅ Генерирует безопасные пароли
- ✅ Запускает все сервисы
- ✅ Проверяет работоспособность

## 📱 Настройка бота

### 1. Получите токен бота

1. Напишите [@BotFather](https://t.me/botfather) в Telegram
2. Команда: `/newbot`
3. Введите имя и username бота
4. Скопируйте токен

### 2. Настройте конфигурацию

```bash
# Отредактируйте .env файл
nano .env

# Измените эти строки:
BOT_TOKEN=ваш_реальный_токен_здесь
BOT_ADMIN_IDS=ваш_telegram_id
```

### 3. Перезапустите бота

```bash
docker compose restart bot
```

## 🎯 Проверка работы

### Посмотреть статус

```bash
docker compose ps
```

### Посмотреть логи

```bash
docker compose logs -f bot
```

### Проверить базу данных

```bash
docker compose exec db psql -U nexusbot -d nexusbot -c "\dt"
```

## 💬 Использование бота

1. **Найдите бота** в Telegram по username
2. **Отправьте** `/start`
3. **Доступные команды**:
   - `/start` - начало работы
   - `/profile` - ваш профиль
   - `/buy` - купить подписку
   - `/help` - справка

## 👑 Админ команды

Если вы указали свой ID в `BOT_ADMIN_IDS`, доступны команды:
- `/admin_stats` - статистика
- `/admin_users` - управление пользователями
- `/admin_bans` - баны

## 🔧 Ручная установка (альтернатива)

Если Docker недоступен:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка БД
python init_db.py

# Запуск
cd nexus_bot && python main.py
```

## 🆘 Проблемы?

### Бот не отвечает
- Проверьте токен в `.env`
- Перезапустите: `docker compose restart bot`

### Ошибка в логах
```bash
docker compose logs bot | tail -20
```

### Очистка и перезапуск
```bash
docker compose down -v
rm -rf data/
./deploy.sh
```

## 📚 Документация

- **[Полная установка](INSTALL.md)** - подробные инструкции
- **[Развертывание](DEPLOY_README.md)** - Docker и продакшн
- **[Архитектура](DEPLOYMENT.md)** - технические детали

## 🎉 Готово!

Ваш VPN-бот теперь работает! 🚀

Присоединяйтесь к сообществу и делитесь отзывами!