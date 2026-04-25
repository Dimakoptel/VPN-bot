# Инструкция по установке и настройке NexusBot

## 📋 Требования

- Python 3.9 или выше
- pip (менеджер пакетов Python)
- Telegram Bot Token (получить у @BotFather)
- SQLite (по умолчанию) или PostgreSQL (опционально)

## 🚀 Установка

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/yourusername/nexus_bot.git
cd nexus_bot
```

### Шаг 2: Создание виртуального окружения (рекомендуется)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка конфигурации

#### 4.1. Создайте файл .env

```bash
cp config/.env.example config/.env
```

#### 4.2. Отредактируйте config/.env

Откройте файл `config/.env` в текстовом редакторе и заполните необходимые значения:

```ini
# === ОБЯЗАТЕЛЬНЫЕ НАСТРОЙКИ ===

# Токен вашего бота от @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# ID администраторов (через запятую, без пробелов)
# Узнать свой ID можно через бота @userinfobot
BOT_ADMIN_IDS=123456789,987654321

# === БАЗА ДАННЫХ ===

# SQLite (по умолчанию)
DATABASE_URL=sqlite+aiosqlite:///nexus_bot.db

# Или PostgreSQL (для продакшена)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nexus_bot

# === ЛИЦЕНЗИЯ ===

# Ключ лицензии (для продакшена)
# Оставьте пустым для режима разработки
LICENSE_KEY=

# URL сервера проверки лицензий (опционально)
LICENSE_SERVER_URL=https://your-license-server.com/validate

# === ПЛАТЕЖИ ===

# Токен платежной системы (YooKassa, Stripe и т.д.)
PAYMENT_PROVIDER_TOKEN=your_payment_token_here

# Валюта по умолчанию
PAYMENT_CURRENCY=RUB

# === VPN ПАНЕЛЬ ===

# URL панели управления VPN (3x-UI, Remnawave и т.д.)
VPN_PANEL_URL=http://localhost:8080

# Логин для доступа к панели
VPN_PANEL_LOGIN=admin

# Пароль для доступа к панели
VPN_PANEL_PASSWORD=secure_password_change_me

# === НАСТРОЙКИ ПРИЛОЖЕНИЯ ===

# Название бота
APP_NAME=NexusBot

# Версия
APP_VERSION=1.0.0

# Username поддержки (без @)
SUPPORT_USERNAME=nexus_support

# === ОПЦИОНАЛЬНО ===

# Redis для кеширования (если используется)
REDIS_URL=redis://localhost:6379/0
```

### Шаг 5: Получение токена бота

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Введите название бота (например, "Nexus VPN Bot")
4. Введите username бота (должен заканчиваться на `bot`, например, `nexus_vpn_bot`)
5. Скопируйте полученный токен и вставьте в `BOT_TOKEN`

### Шаг 6: Узнайте свой Telegram ID

1. Найдите бота @userinfobot
2. Отправьте ему любое сообщение
3. Скопируйте ваш ID и добавьте в `BOT_ADMIN_IDS`

## 🔐 Генерация ключа лицензии (для продакшена)

Если вы планируете распространять бота коммерчески, сгенерируйте ключ лицензии:

```python
# generate_license.py
from licenses.manager import LicenseManager

manager = LicenseManager()

# Создать лицензию PROFESSIONAL
key = manager.generate_license(
    license_type="PROFESSIONAL",
    max_users=10000,
    valid_days=365,
    description="Лицензия для клиента X"
)

print(f"Ваш ключ лицензии: {key}")
```

Запустите скрипт:
```bash
python generate_license.py
```

Скопируйте полученный ключ в `LICENSE_KEY` в файле `.env`.

## ▶️ Запуск бота

### Обычный запуск

```bash
python main.py
```

### Запуск в режиме отладки

```bash
python -u main.py
```

### Запуск в фоне (Linux)

```bash
nohup python main.py > bot.log 2>&1 &
```

### Использование systemd (Linux, для продакшена)

Создайте файл `/etc/systemd/system/nexusbot.service`:

```ini
[Unit]
Description=NexusBot Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/nexus_bot
Environment="PATH=/path/to/nexus_bot/venv/bin"
ExecStart=/path/to/nexus_bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Активируйте и запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexusbot
sudo systemctl start nexusbot
sudo systemctl status nexusbot
```

## ✅ Проверка работы

1. Откройте вашего бота в Telegram
2. Отправьте команду `/start`
3. Бот должен ответить приветственным сообщением
4. Для администраторов доступна команда `/admin`

## 🔧 Дополнительные настройки

### Логирование

Логи сохраняются в файл `logs/bot.log`. Для просмотра:

```bash
tail -f logs/bot.log
```

### Резервное копирование базы данных

```bash
# SQLite
cp nexus_bot.db nexus_bot_backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump -U user nexus_bot > backup_$(date +%Y%m%d).sql
```

### Обновление бота

```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart nexusbot
```

## ❓ Решение проблем

### Бот не запускается

1. Проверьте правильность токена в `.env`
2. Убедитесь, что все зависимости установлены: `pip install -r requirements.txt`
3. Проверьте логи: `cat logs/bot.log`

### Ошибка лицензии

- Для режима разработки оставьте `LICENSE_KEY` пустым
- Для продакшена убедитесь, что ключ сгенерирован правильно

### Бот не отвечает на команды

1. Проверьте, добавлен ли ваш ID в `BOT_ADMIN_IDS`
2. Перезапустите бота
3. Проверьте логи на наличие ошибок

## 📞 Поддержка

Если возникли проблемы:

- Документация: [README.md](README.md)
- GitHub Issues: https://github.com/yourusername/nexus_bot/issues
- Telegram: @nexus_support

---

**NexusBot v1.0.0** | © 2024 NexusBot
