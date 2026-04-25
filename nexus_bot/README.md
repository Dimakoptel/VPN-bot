# NexusBot - Telegram Bot для управления подписками

🚀 Современный бот для управления VPN подписками с системой лицензирования и защиты от нелегального использования.

## 📋 Особенности

- ✅ **Полностью свой код** - написан с нуля, не нарушает лицензию CC BY-NC оригинального SoloBot
- 🔐 **Система лицензий** - защита от коммерческого использования без разрешения
- 👥 **Управление пользователями** - баны, теневые баны, реферальная система
- 💳 **Подписки** - тарифы, платежи, продление
- 📊 **Админ-панель** - статистика, управление пользователями, аудит
- 🛡️ **Audit Log** - журнал всех действий администраторов
- 🌐 **Гибкая интеграция** - поддержка 3x-UI, Remnawave или собственных панелей

## 🏗️ Структура проекта

```
nexus_bot/
├── config/              # Конфигурация и настройки
│   ├── __init__.py
│   ├── settings.py      # Pydantic настройки
│   └── .env.example     # Пример переменных окружения
├── core/                # Ядро приложения
│   └── database.py      # Менеджер базы данных
├── handlers/            # Обработчики команд
│   ├── __init__.py
│   ├── user/            # Команды пользователей
│   │   ├── __init__.py
│   │   ├── start.py     # /start
│   │   ├── profile.py   # /profile
│   │   ├── buy.py       # /buy
│   │   └── help.py      # /help
│   └── admin/           # Команды администраторов
│       ├── __init__.py
│       ├── bans.py      # Управление банами
│       ├── users.py     # Управление пользователями
│       ├── stats.py     # Статистика
│       └── license.py   # Управление лицензиями
├── models/              # SQLAlchemy модели
│   ├── __init__.py
│   └── database.py      # Модели: User, Subscription, License, Ban, AuditLog
├── middleware/          # Middleware
│   ├── __init__.py
│   └── ban_checker.py   # Проверка банов и лицензий
├── services/            # Бизнес-логика
│   ├── __init__.py
│   ├── user_service.py  # Сервис пользователей
│   ├── subscription_service.py  # Подписки
│   └── vpn_service.py   # Интеграция с VPN панелями
├── licenses/            # Система лицензирования
│   ├── __init__.py
│   └── manager.py       # Менеджер лицензий
├── utils/               # Утилиты
│   ├── logger.py        # Настройка логгера
│   └── keyboard.py      # Клавиатуры
├── web/                 # Webhook/API (опционально)
├── tests/               # Тесты
├── main.py              # Точка входа
├── requirements.txt     # Зависимости
└── LICENSE              # Лицензионное соглашение
```

## 🚀 Быстрый старт

### 1. Требования

- Python 3.9+
- SQLite (по умолчанию) или PostgreSQL
- Telegram Bot Token

### 2. Установка зависимостей

```bash
cd nexus_bot
pip install -r requirements.txt
```

### 3. Настройка

Скопируйте `.env.example` в `.env`:

```bash
cp config/.env.example config/.env
```

Отредактируйте `config/.env`:

```ini
# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_ADMIN_IDS=123456789,987654321

# Database
DATABASE_URL=sqlite+aiosqlite:///nexus_bot.db

# License (для продакшена)
LICENSE_KEY=your_license_key_here

# Payment Provider
PAYMENT_PROVIDER_TOKEN=your_payment_token
PAYMENT_CURRENCY=RUB

# VPN Panel Integration
VPN_PANEL_URL=http://localhost:8080
VPN_PANEL_LOGIN=admin
VPN_PANEL_PASSWORD=secure_password

# App Settings
APP_NAME=NexusBot
APP_VERSION=1.0.0
SUPPORT_USERNAME=@nexus_support
```

### 4. Запуск

```bash
python main.py
```

## 📝 Команды

### Для пользователей:
| Команда | Описание |
|---------|----------|
| `/start` | Запустить бота, регистрация |
| `/profile` | Профиль пользователя, статус подписки |
| `/buy` | Купить подписку, выбор тарифа |
| `/help` | Помощь, информация о боте |
| `/support` | Связаться с поддержкой |
| `/referral` | Реферальная программа |

### Для администраторов:
| Команда | Описание |
|---------|----------|
| `/admin` | Админ-панель |
| `/ban` | Забанить пользователя |
| `/unban` | Разбанить пользователя |
| `/shadowban` | Теневой бан |
| `/users` | Список пользователей |
| `/stats` | Общая статистика |
| `/license` | Создать ключ лицензии |
| `/audit` | Журнал аудита |
| `/broadcast` | Рассылка сообщений |

## 🔐 Система лицензий

Для защиты от нелегального коммерческого использования:

### Как это работает:

1. **Генерация ключа**: 
   - Разработчик генерирует уникальный ключ
   - Ключ привязывается к домену/серверу
   - Устанавливаются лимиты (активации, срок действия)

2. **Активация**: 
   - Ключ добавляется в `.env` файл (`LICENSE_KEY`)
   - При запуске бот проверяет валидность

3. **Проверка**:
   - Локальная проверка формата и подписи
   - Опционально: проверка на сервере разработчика
   - Блокировка при невалидной лицензии

4. **Ограничения**:
   - Лимит активаций на ключ
   - Срок действия лицензии
   - Привязка к IP/домену

### Типы лицензий:

| Тип | Описание |
|-----|----------|
| `DEVELOPMENT` | Для тестирования, без ограничений |
| `STANDARD` | Стандартная, до 1000 пользователей |
| `PROFESSIONAL` | Расширенная, до 10000 пользователей |
| `ENTERPRISE` | Без ограничений, приоритетная поддержка |

### Генерация ключа (пример):

```python
from licenses.manager import LicenseManager

manager = LicenseManager()
key = manager.generate_license(
    license_type="PROFESSIONAL",
    max_users=10000,
    valid_days=365
)
print(f"Ваш ключ: {key}")
```

## 🛡️ Система безопасности

### Типы блокировок:

| Тип | Описание |
|-----|----------|
| 🚫 **Обычный бан** | Пользователь видит сообщение о блокировке |
| 👻 **Теневой бан** | Действия пользователя игнорируются, он не знает о бане |
| ⏰ **Временный бан** | Автоматическая разблокировка по истечении срока |

### Audit Log:

Все действия администраторов записываются:
- Кто забанил пользователя
- Кто создал лицензию
- Кто изменил настройки
- Время и причина действия

Пример просмотра аудита:
```
/admin audit --user_id 123456789
```

## 📦 Расширение функционала

Проект модульный - легко добавить новые функции:

### 1. Добавить платежную систему:

Создайте `services/payment_service.py`:

```python
class PaymentService:
    async def create_payment(self, user_id, amount):
        # Ваша логика оплаты
        pass
    
    async def verify_payment(self, payment_id):
        # Проверка статуса оплаты
        pass
```

### 2. Интеграция с VPN панелью:

Создайте `services/vpn_service.py`:

```python
class VPNService:
    def __init__(self, panel_url, login, password):
        self.panel_url = panel_url
        # Инициализация подключения
    
    async def create_key(self, user_id, days):
        # Создание ключа доступа
        pass
    
    async def revoke_key(self, user_id):
        # Отзыв ключа
        pass
```

### 3. Добавить рассылки:

Создайте `handlers/admin/broadcast.py`:

```python
@router.callback_query(F.data == "admin_broadcast")
async def broadcast_handler(callback: CallbackQuery):
    # Логика рассылки
    pass
```

## 🧪 Тестирование

Запуск тестов:

```bash
pytest tests/ -v
```

Пример теста:

```python
# tests/test_user_service.py
async def test_create_user():
    service = UserService()
    user = await service.create_user(tg_id=123456789)
    assert user.tg_id == 123456789
```

## 📄 Лицензия

Этот проект является **оригинальной разработкой** и не нарушает лицензию CC BY-NC 4.0 оригинального SoloBot.

Вы можете использовать этот код в коммерческих целях, так как он написан с нуля без копирования чужого кода.

**Важно**: 
- Не копируйте код из оригинального SoloBot
- Используйте только идеи и концепции как вдохновение
- Все реализации написаны независимо

## 🤝 Поддержка

- Документация: [Ссылка на docs]
- Вопросы: `@nexus_support`
- GitHub Issues: [Ссылка на issues]

## 📈 Roadmap

- [ ] Интеграция с YooKassa/Stripe
- [ ] Поддержка 3x-UI панели
- [ ] Веб-админка
- [ ] Мобильное приложение
- [ ] Мультиязычность

---

**NexusBot v1.0.0** - Создан с нуля для легального коммерческого использования.

© 2024 NexusBot. Все права защищены.
