# Инструкция по установке и настройке NexusBot

## 📋 Требования

### Минимальные требования:
- **ОС**: Linux, macOS, Windows
- **Python**: 3.11 или выше
- **RAM**: 512 MB (рекомендуется 1 GB)
- **Диск**: 1 GB свободного места

### Для Docker развертывания:
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Для ручной установки:
- **Python**: 3.11+
- **pip**: последняя версия
- **Telegram Bot Token** (от @BotFather)

## 🆓 Лицензия

NexusBot — это **свободное программное обеспечение** под лицензией MIT:
- ✅ Коммерческое использование разрешено
- ✅ Модификация кода разрешена
- ✅ Распространение разрешена
- ✅ Система лицензий опциональна (можно отключить)

## 🚀 Установка

### Вариант 1: Docker (рекомендуется)

#### Автоматическое развертывание

```bash
# Клонирование
git clone https://github.com/Dimakoptel/VPN-bot.git
cd VPN-bot

# Автоматический запуск
./deploy.sh
```

Скрипт автоматически:
- Создаст конфигурационные файлы
- Соберет Docker образы
- Запустит PostgreSQL, Redis и бота
- Инициализирует базу данных

#### Ручное Docker развертывание

```bash
# Клонирование
git clone https://github.com/Dimakoptel/VPN-bot.git
cd VPN-bot

# Запуск стека
docker compose up --build -d

# Проверка
docker compose ps
docker compose logs bot
```

### Вариант 2: Ручная установка

#### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Dimakoptel/VPN-bot.git
cd VPN-bot
```

#### Шаг 2: Создание виртуального окружения (рекомендуется)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

#### Шаг 4: Настройка конфигурации

##### 4.1. Создайте файл .env

```bash
cp nexus_bot/config/.env.example nexus_bot/config/.env
```

##### 4.2. Отредактируйте .env файл

```env
# Bot Configuration
BOT_TOKEN=ваш_токен_от_BotFather
BOT_ADMIN_IDS=ваш_telegram_id

# Database (SQLite для разработки)
DATABASE_URL=sqlite+aiosqlite:///nexus_bot.db

# Другие настройки по необходимости...
```

##### 4.3. Инициализация базы данных

```bash
python init_db.py
```

#### Шаг 5: Запуск бота

```bash
cd nexus_bot
python main.py
```

## ⚙️ Конфигурация

### Основные настройки

| Переменная | Описание | Пример |
|------------|----------|---------|
| `BOT_TOKEN` | Токен от @BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `BOT_ADMIN_IDS` | ID администраторов | `123456789,987654321` |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///nexus_bot.db` |
| `REDIS_URL` | URL Redis | `redis://localhost:6379/0` |

### Полный список настроек

См. файл `nexus_bot/config/.env.example`

## 🗄️ Работа с базой данных

### SQLite (по умолчанию)

```bash
# Инициализация
python init_db.py

# Просмотр таблиц
sqlite3 nexus_bot.db ".tables"
```

### PostgreSQL (продакшн)

```bash
# В Docker (автоматически)
./deploy.sh

# Или вручную
docker run -d --name postgres \
  -e POSTGRES_DB=nexusbot \
  -e POSTGRES_USER=nexusbot \
  -e POSTGRES_PASSWORD=your_password \
  postgres:15-alpine
```

## 🔧 Устранение неполадок

### Бот не запускается

1. **Проверьте токен**:
   ```bash
   # Токен должен быть валидным
   python -c "from aiogram.utils.token import validate_token; validate_token('ВАШ_ТОКЕН')"
   ```

2. **Проверьте зависимости**:
   ```bash
   pip list | grep aiogram
   ```

3. **Проверьте логи**:
   ```bash
   python main.py 2>&1 | head -20
   ```

### Проблемы с базой данных

1. **SQLite**:
   ```bash
   # Удалить и пересоздать
   rm nexus_bot.db
   python init_db.py
   ```

2. **PostgreSQL**:
   ```bash
   # Проверить подключение
   docker compose exec db psql -U nexusbot -d nexusbot -c "SELECT 1"
   ```

### Docker проблемы

```bash
# Очистка
docker compose down -v
docker system prune -f

# Пересборка
docker compose up --build --force-recreate
```

## 📊 Мониторинг

### Логи

```bash
# Docker
docker compose logs -f bot

# Ручная установка
tail -f logs/bot.log
```

### Метрики Prometheus

```bash
# Доступны на порту 9090
curl http://localhost:9090/metrics
```

## 🔄 Обновление

```bash
# Получить обновления
git pull origin main

# Docker
docker compose down
docker compose pull
docker compose up -d

# Ручная установка
pip install -r requirements.txt --upgrade
python main.py
```

## 📞 Поддержка

- **Документация**: [README.md](README.md)
- **Развертывание**: [DEPLOY_README.md](DEPLOY_README.md)
- **Issues**: [GitHub Issues](https://github.com/Dimakoptel/VPN-bot/issues)

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

## 🔐 Генерация ключа лицензии (ОПЦИОНАЛЬНО)

> ⚠️ **Важно**: Система лицензий полностью опциональна! Вы можете использовать бота без неё.

Если вы хотите защитить свои модификации или распространять бота с ограничениями, сгенерируйте ключ лицензии:

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

Скопируйте полученный ключ в `LICENSE_KEY` в файле `.env` и установите `LICENSE_CHECK_ENABLED=true`.

### Отключение системы лицензий

Для полного отключения просто убедитесь, что в `.env`:

```ini
LICENSE_KEY=
LICENSE_CHECK_ENABLED=false
```

Бот будет работать без каких-либо ограничений и проверок.

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

- Система лицензий опциональна — для свободного использования оставьте `LICENSE_KEY` пустым
- Установите `LICENSE_CHECK_ENABLED=false` для полного отключения проверок
- Если используете лицензию, убедитесь, что ключ сгенерирован правильно

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

**NexusBot v1.0.0** | © 2024 NexusBot Community | Свободное ПО под лицензией MIT
