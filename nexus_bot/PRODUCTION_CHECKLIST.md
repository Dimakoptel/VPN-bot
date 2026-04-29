# 📋 Чеклист для запуска NexusBot в продакшен

## ✅ Выполнено (готово к работе)

### 1. База данных
- [x] Настроена поддержка SQLite (для разработки/тестирования)
- [x] Настроена поддержка PostgreSQL (для продакшена)
- [x] Все модели SQLAlchemy исправлены и работают
- [x] Менеджер баз данных инициализируется корректно

### 2. Логирование
- [x] Настроено логирование с ротацией файлов
- [x] Уровень логирования: INFO (можно изменить на WARNING/ERROR для продакшена)
- [x] Максимальный размер файла: 10 MB
- [x] Количество резервных копий: 5
- [x] Путь к логам: `/var/log/nexusbot/bot.log`
- [x] Логи пишутся и в консоль, и в файл

### 3. Мониторинг
- [x] Интеграция с Prometheus готова
- [x] Метрики для сообщений, пользователей, лицензий, ошибок, платежей
- [x] По умолчанию отключен (включить через `PROMETHEUS_ENABLED=true`)

### 4. Конфигурация
- [x] Файл `.env` создан и настроен
- [x] Pydantic-settings используется для валидации конфигурации
- [x] Путь к `.env` файлу указан абсолютно (через `Path(__file__).parent`)

---

## ⚠️ ТРЕБУЕТСЯ ВНИМАНИЯ (обязательно перед запуском)

### 1. Telegram Bot Token
```ini
BOT_TOKEN=your_real_telegram_bot_token_here
```
**Где получить:** [@BotFather](https://t.me/BotFather) в Telegram

### 2. Admin IDs
```ini
BOT_ADMIN_IDS=your_telegram_id,second_admin_id
```
**Где получить:** Узнайте свой ID через бота [@userinfobot](https://t.me/userinfobot)

### 3. Для продакшена - переключитесь на PostgreSQL

#### Вариант A: Docker с PostgreSQL
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: nexusbot
      POSTGRES_USER: nexusbot
      POSTGRES_PASSWORD: secure_password_change_me
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  bot:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql+asyncpg://nexusbot:secure_password_change_me@postgres:5432/nexusbot

volumes:
  postgres_data:
```

#### Вариант B: Обновите .env
```ini
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/nexusbot
```

### 4. Безопасность
- [ ] Смените все пароли по умолчанию (`change_me`, `secure_password`)
- [ ] Используйте надежные токены и ключи
- [ ] Ограничьте доступ к `.env` файлу (chmod 600)
- [ ] Не коммитьте `.env` в git (добавлен в `.gitignore`)

### 5. Лицензия (опционально)
```ini
LICENSE_KEY=your_license_key_here
```

### 6. Платежи (опционально)
```ini
PAYMENT_PROVIDER_TOKEN=your_yookassa_or_stripe_token
```

### 7. VPN Panel (опционально)
```ini
VPN_PANEL_URL=https://your-vpn-panel.com
VPN_PANEL_LOGIN=admin
VPN_PANEL_PASSWORD=secure_password_change_me
```

---

## 🚀 Запуск бота

### Быстрый старт (SQLite, для тестирования)
```bash
cd /workspace/nexus_bot
python main.py
```

### Продакшен запуск

#### 1. Установите зависимости
```bash
pip install -r requirements.txt
```

#### 2. Настройте .env
Отредактируйте `/workspace/nexus_bot/config/.env` с реальными значениями

#### 3. Переключитесь на PostgreSQL (рекомендуется)
```ini
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/nexusbot
```

#### 4. Запустите
```bash
cd /workspace/nexus_bot
python main.py
```

#### 5. Или через systemd (Linux)
```ini
# /etc/systemd/system/nexusbot.service
[Unit]
Description=NexusBot Telegram Bot
After=network.target

[Service]
Type=simple
User=nexusbot
WorkingDirectory=/opt/nexusbot
Environment="PATH=/opt/nexusbot/venv/bin"
ExecStart=/opt/nexusbot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable nexusbot
sudo systemctl start nexusbot
sudo systemctl status nexusbot
```

---

## 📊 Мониторинг и логи

### Просмотр логов
```bash
tail -f /var/log/nexusbot/bot.log
```

### Включение Prometheus метрик
В `.env`:
```ini
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

Метрики будут доступны по адресу: `http://localhost:9090/metrics`

### Примеры метрик
- `nexusbot_messages_total` - всего обработано сообщений
- `nexusbot_active_users` - количество активных пользователей
- `nexusbot_banned_users` - количество заблокированных пользователей
- `nexusbot_errors_total` - количество ошибок
- `nexusbot_payments_total` - количество платежей

---

## 🔧 Диагностика проблем

### Бот не запускается
1. Проверьте токен бота в `.env`
2. Проверьте подключение к базе данных
3. Посмотрите логи: `cat /var/log/nexusbot/bot.log`

### Ошибки базы данных
- Для SQLite: проверьте права на запись в директорию
- Для PostgreSQL: проверьте что сервер запущен и учетные данные верны

### Ошибки авторизации в Telegram
- Токен бота неверный или отозван
- Получите новый токен у @BotFather

---

## 📁 Структура проекта

```
nexus_bot/
├── config/
│   ├── settings.py       # Настройки (pydantic)
│   └── .env              # Переменные окружения
├── core/
│   └── database.py       # Менеджер БД
├── models/
│   └── database.py       # SQLAlchemy модели
├── services/
│   └── user_service.py   # Бизнес-логика
├── middleware/
│   └── ban_checker.py    # Middleware
├── handlers/
│   ├── user/             # Хендлеры пользователей
│   └── admin/            # Хендлеры администратора
├── licenses/
│   └── manager.py        # Система лицензий
├── utils/
│   ├── logging_config.py # Настройка логирования
│   └── monitoring.py     # Prometheus метрики
├── main.py               # Точка входа
└── requirements.txt      # Зависимости
```

---

## ✅ Итоговый статус

**Проект ГОТОВ к запуску** после выполнения следующих шагов:

1. ✅ ~~Настройка базы данных~~ (SQLite работает, PostgreSQL готов)
2. ✅ ~~Настройка логирования~~ (работает)
3. ✅ ~~Настройка мониторинга~~ (готов, отключен по умолчанию)
4. ⚠️ **Указать реальный BOT_TOKEN**
5. ⚠️ **Указать реальные BOT_ADMIN_IDS**
6. ⚠️ **Для продакшена: переключиться на PostgreSQL**
7. ⚠️ **Сменить пароли по умолчанию**

После выполнения шагов 4-7 бот готов к работе в продакшене!
