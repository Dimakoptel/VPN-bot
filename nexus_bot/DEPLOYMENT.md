# 🚀 Подробная инструкция по развертыванию и запуску NexusBot

Эта инструкция описывает полный процесс установки, настройки и запуска бота **NexusBot** на различных платформах (локально, VPS, Docker).

---

## 📋 Содержание

1. [Требования к системе](#-требования-к-системе)
2. [Подготовка окружения](#-подготовка-окружения)
3. [Установка зависимостей](#-установка-зависимостей)
4. [Настройка конфигурации](#-настройка-конфигурации)
5. [Инициализация базы данных](#-инициализация-базы-данных)
6. [Генерация лицензионного ключа](#-генерация-лицензионного-ключа)
7. [Запуск бота](#-запуск-бота)
8. [Запуск через Docker](#-запуск-через-docker)
9. [Настройка автозапуска (Systemd)](#-настройка-автозапуска-systemd)
10. [Проверка работоспособности](#-проверка-работоспособности)
11. [Обновление бота](#-обновление-бота)
12. [Решение проблем](#-решение-проблем)

---

## 🔧 Требования к системе

### Минимальные требования:
- **ОС**: Linux (Ubuntu 20.04+, Debian 11+), macOS, Windows 10/11
- **CPU**: 1 ядро
- **RAM**: 512 MB (рекомендуется 1 GB)
- **Диск**: 1 GB свободного места
- **Python**: 3.9 или выше
- **База данных**: SQLite (встроена) или PostgreSQL (опционально)
- **Интернет**: Стабильное подключение для работы с Telegram API

### Для производства (рекомендуется):
- **ОС**: Ubuntu 22.04 LTS
- **CPU**: 2 ядра
- **RAM**: 2 GB
- **Диск**: 10 GB SSD
- **Домен**: Для webhook (опционально)
- **SSL**: Сертификат для HTTPS (если используется webhook)

---

## 🛠 Подготовка окружения

### Вариант 1: Локальная разработка (Linux/macOS)

```bash
# Обновление пакетов
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install -y python3 python3-pip python3-venv git curl

# Проверка версии Python
python3 --version  # Должна быть 3.9+
```

### Вариант 2: Сервер (VPS)

```bash
# Подключение к серверу
ssh user@your-server-ip

# Создание пользователя для бота (рекомендуется)
sudo adduser nexusbot
sudo usermod -aG sudo nexusbot

# Переключение на пользователя
su - nexusbot
```

### Вариант 3: Windows

1. Скачайте и установите Python с [официального сайта](https://www.python.org/downloads/)
2. Установите Git с [официального сайта](https://git-scm.com/download/win)
3. Откройте PowerShell от имени администратора:
```powershell
# Проверка версий
python --version
git --version
```

---

## 📦 Установка зависимостей

### Шаг 1: Клонирование репозитория

```bash
# Перейдите в директорию для проекта
cd /opt  # или любую другую директорию

# Клонируйте репозиторий
git clone <URL_ВАШЕГО_РЕПОЗИТОРИЯ> nexus_bot
cd nexus_bot
```

*Если у вас нет репозитория, создайте структуру вручную:*
```bash
mkdir -p nexus_bot/{config,core,handlers,models,middleware,services,utils,licenses,web,tests,data,logs}
cd nexus_bot
```

### Шаг 2: Создание виртуального окружения

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
# Для Linux/macOS:
source venv/bin/activate

# Для Windows:
# venv\Scripts\activate
```

### Шаг 3: Установка пакетов

```bash
# Обновление pip
pip install --upgrade pip

# Установка зависимостей
pip install -r requirements.txt
```

*Если файла `requirements.txt` нет, создайте его:*
```bash
cat > requirements.txt << EOF
aiogram>=3.0.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
cryptography>=40.0.0
aiohttp>=3.8.0
apscheduler>=3.10.0
logging>=0.4.9.6
EOF

pip install -r requirements.txt
```

---

## ⚙️ Настройка конфигурации

### Шаг 1: Создание файла окружения

```bash
# Копирование шаблона
cp .env.example .env

# Или создание вручную
cat > .env << EOF
# Telegram Bot Token (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# ID владельца бота (супер-админ)
OWNER_ID=123456789

# Режим работы (development/production)
ENVIRONMENT=development

# База данных
DATABASE_URL=sqlite+aiosqlite:///data/nexus_bot.db

# Лицензионный ключ (генерируется отдельно)
LICENSE_KEY=your_license_key_here

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Вебхук (опционально)
WEBHOOK_URL=
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8080
EOF
```

### Шаг 2: Получение токена бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Придумайте имя и юзернейм для бота
4. Скопируйте полученный токен
5. Вставьте токен в файл `.env` вместо `your_bot_token_here`

### Шаг 3: Получение Owner ID

1. Запустите бота и отправьте ему любое сообщение
2. Найдите бота [@userinfobot](https://t.me/userinfobot) или аналогичный
3. Узнайте свой числовой ID
4. Вставьте ID в файл `.env` вместо `123456789`

---

## 💾 Инициализация базы данных

### Автоматическая инициализация

База данных создается автоматически при первом запуске бота.

### Ручная инициализация (опционально)

```bash
# Запуск скрипта инициализации
python -m scripts.init_db
```

*Или создайте скрипт `scripts/init_db.py`:*
```python
import asyncio
from models.base import Base, engine

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных успешно инициализирована")

if __name__ == "__main__":
    asyncio.run(init_db())
```

### Проверка базы данных

```bash
# Проверка наличия файла БД
ls -la data/

# Должен появиться файл: nexus_bot.db
```

---

## 🔑 Генерация лицензионного ключа

### Шаг 1: Запуск генератора

```bash
# Запуск скрипта генерации
python -m licenses.generate_key
```

*Или создайте скрипт `licenses/generate_key.py`:*
```python
import secrets
import hashlib
from datetime import datetime

def generate_license_key(owner_id: str) -> str:
    """Генерация уникального лицензионного ключа"""
    timestamp = datetime.now().isoformat()
    random_part = secrets.token_hex(16)
    unique_string = f"{owner_id}{timestamp}{random_part}"
    license_hash = hashlib.sha256(unique_string.encode()).hexdigest()
    
    # Форматирование ключа: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
    key_parts = [license_hash[i:i+4] for i in range(0, 24, 4)]
    return "-".join(key_parts).upper()

if __name__ == "__main__":
    owner_id = input("Введите Owner ID: ").strip()
    if not owner_id.isdigit():
        print("❌ Owner ID должен быть числом")
        exit(1)
    
    key = generate_license_key(owner_id)
    print(f"\n✅ Ваш лицензионный ключ:\n{key}")
    print("\n📝 Сохраните этот ключ в файл .env переменную LICENSE_KEY")
```

### Шаг 2: Активация лицензии

1. Скопируйте сгенерированный ключ
2. Откройте файл `.env`
3. Замените `your_license_key_here` на ваш ключ
4. Сохраните файл

### Шаг 3: Проверка лицензии

При запуске бот автоматически проверит лицензию. Если ключ недействителен, бот не запустится.

---

## ▶️ Запуск бота

### Режим разработки

```bash
# Активация виртуального окружения
source venv/bin/activate

# Запуск бота
python main.py
```

### Режим производства

```bash
# Использование nohup для работы в фоне
nohup python main.py > logs/bot_output.log 2>&1 &

# Проверка процесса
ps aux | grep main.py

# Просмотр логов в реальном времени
tail -f logs/bot_output.log
```

### С разными уровнями логирования

```bash
# DEBUG (подробные логи)
LOG_LEVEL=DEBUG python main.py

# INFO (стандартные логи)
LOG_LEVEL=INFO python main.py

# WARNING (только предупреждения и ошибки)
LOG_LEVEL=WARNING python main.py
```

---

## 🐳 Запуск через Docker

### Шаг 1: Создание Dockerfile

Создайте файл `Dockerfile` в корне проекта:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python-пакетов
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий для данных и логов
RUN mkdir -p data logs

# Переменная окружения
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "main.py"]
```

### Шаг 2: Создание docker-compose.yml

Создайте файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  nexusbot:
    build: .
    container_name: nexus_bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - nexus_network

networks:
  nexus_network:
    driver: bridge
```

### Шаг 3: Запуск через Docker Compose

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f nexusbot

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление образа
docker-compose pull
docker-compose up -d --build
```

### Шаг 4: Мониторинг контейнера

```bash
# Статус контейнера
docker ps

# Использование ресурсов
docker stats nexus_bot

# Вход в контейнер
docker exec -it nexus_bot bash
```

---

## 🔧 Настройка автозапуска (Systemd)

Для автоматического запуска бота при перезагрузке сервера:

### Шаг 1: Создание service-файла

```bash
sudo nano /etc/systemd/system/nexusbot.service
```

### Шаг 2: Добавление конфигурации

```ini
[Unit]
Description=NexusBot Telegram Bot
After=network.target

[Service]
Type=simple
User=nexusbot
WorkingDirectory=/opt/nexus_bot
Environment="PATH=/opt/nexus_bot/venv/bin"
ExecStart=/opt/nexus_bot/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/nexus_bot/logs/bot_systemd.log
StandardError=append:/opt/nexus_bot/logs/bot_systemd_error.log

# Лимиты ресурсов
LimitNOFILE=65535
Nice=10

[Install]
WantedBy=multi-user.target
```

### Шаг 3: Активация службы

```bash
# Перезагрузка демонов systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable nexusbot

# Запуск службы
sudo systemctl start nexusbot

# Проверка статуса
sudo systemctl status nexusbot

# Просмотр логов
sudo journalctl -u nexusbot -f

# Остановка службы
sudo systemctl stop nexusbot

# Перезапуск службы
sudo systemctl restart nexusbot
```

---

## ✅ Проверка работоспособности

### Шаг 1: Проверка процессов

```bash
# Для обычного запуска
ps aux | grep main.py

# Для systemd
sudo systemctl status nexusbot

# Для Docker
docker ps | grep nexus_bot
```

### Шаг 2: Проверка логов

```bash
# Логи приложения
tail -f logs/bot.log

# Логи вывода
tail -f logs/bot_output.log

# Логи systemd
sudo journalctl -u nexusbot -n 50
```

### Шаг 3: Тестирование бота

1. Откройте Telegram
2. Найдите вашего бота по юзернейму
3. Отправьте команду `/start`
4. Бот должен ответить приветственным сообщением

### Шаг 4: Проверка админ-панели

Отправьте команду `/admin` (только для Owner ID):
- Должна открыться админ-панель
- Доступны команды управления пользователями, лицензиями, рассылками

### Шаг 5: Проверка лицензии

Бот должен вывести информацию о лицензии при запуске:
```
✅ Лицензия активна
Ключ: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
Владелец: 123456789
Дата активации: 2024-01-01
```

---

## 🔄 Обновление бота

### Обновление из Git

```bash
# Переход в директорию проекта
cd /opt/nexus_bot

# Активация виртуального окружения
source venv/bin/activate

# Получение обновлений
git pull origin main

# Установка новых зависимостей
pip install -r requirements.txt --upgrade

# Перезапуск бота
# Для systemd:
sudo systemctl restart nexusbot

# Для Docker:
docker-compose up -d --build

# Для ручного запуска:
# Остановите текущий процесс и запустите заново
```

### Резервное копирование перед обновлением

```bash
# Создание резервной копии
BACKUP_DIR="/opt/backups/nexus_bot_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r /opt/nexus_bot/data $BACKUP_DIR/
cp /opt/nexus_bot/.env $BACKUP_DIR/

echo "✅ Резервная копия создана: $BACKUP_DIR"
```

---

## 🛠 Решение проблем

### Проблема 1: Бот не запускается

**Симптомы:** Ошибки при запуске, бот не отвечает

**Решение:**
```bash
# Проверка логов
tail -f logs/bot.log

# Проверка токена
grep BOT_TOKEN .env

# Проверка подключения к интернету
ping api.telegram.org

# Проверка прав доступа
ls -la data/
chmod 755 data/
```

### Проблема 2: Ошибка лицензии

**Симптомы:** "Недействительный лицензионный ключ"

**Решение:**
```bash
# Проверка ключа в .env
grep LICENSE_KEY .env

# Перегенерация ключа
python -m licenses.generate_key

# Проверка формата ключа (должен быть XXXX-XXXX-...)
```

### Проблема 3: База данных повреждена

**Симптомы:** Ошибки SQLAlchemy, бот падает

**Решение:**
```bash
# Резервное копирование текущей БД
cp data/nexus_bot.db data/nexus_bot.db.backup

# Удаление поврежденной БД
rm data/nexus_bot.db

# Перезапуск бота (БД создастся заново)
# Внимание: данные будут потеряны!
```

### Проблема 4: Бот не отвечает на команды

**Симптомы:** Бот онлайн, но не реагирует

**Решение:**
```bash
# Проверка длинного поллинга
# Убедитесь, что не используется webhook одновременно

# Перезапуск бота
sudo systemctl restart nexusbot

# Проверка лимитов Telegram API
# Не более 30 сообщений в секунду
```

### Проблема 5: Утечка памяти

**Симптомы:** Постепенный рост потребления RAM

**Решение:**
```bash
# Настройка перезапуска по расписанию в systemd
# Добавьте в nexusbot.service:
RuntimeMaxSec=86400  # Перезапуск каждые 24 часа

# Или используйте Docker с ограничением памяти
# В docker-compose.yml добавьте:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

### Проблема 6: Ошибки при установке зависимостей

**Симптомы:** `pip install` завершается с ошибкой

**Решение:**
```bash
# Обновление pip
pip install --upgrade pip setuptools wheel

# Установка системных зависимостей (Ubuntu/Debian)
sudo apt install -y python3-dev libffi-dev libssl-dev

# Очистка кэша pip
pip cache purge

# Установка без кэша
pip install --no-cache-dir -r requirements.txt
```

---

## 📊 Мониторинг и обслуживание

### Настройка мониторинга

#### Использование Prometheus + Grafana (опционально)

1. Установите экспортер для Python
2. Настройте сбор метрик
3. Визуализируйте в Grafana

#### Простой мониторинг через скрипт

Создайте `scripts/health_check.sh`:

```bash
#!/bin/bash

BOT_NAME="nexusbot"
LOG_FILE="/opt/nexus_bot/logs/bot.log"
ALERT_EMAIL="admin@example.com"

# Проверка процесса
if ! pgrep -f "python.*main.py" > /dev/null; then
    echo "❌ Бот не работает!" | mail -s "Alert: NexusBot Down" $ALERT_EMAIL
    sudo systemctl restart $BOT_NAME
fi

# Проверка места на диске
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️ Место на диске заканчивается: ${DISK_USAGE}%" | mail -s "Alert: Disk Space" $ALERT_EMAIL
fi

# Проверка размера логов
LOG_SIZE=$(du -m $LOG_FILE | cut -f1)
if [ $LOG_SIZE -gt 100 ]; then
    # Ротация логов
    mv $LOG_FILE ${LOG_FILE}.$(date +%Y%m%d)
    gzip ${LOG_FILE}.$(date +%Y%m%d)
    sudo systemctl restart $BOT_NAME
fi
```

Добавьте в crontab:
```bash
crontab -e

# Проверка каждые 5 минут
*/5 * * * * /opt/nexus_bot/scripts/health_check.sh
```

---

## 🎯 Чек-лист после установки

- [ ] Бот отвечает на команду `/start`
- [ ] Админ-панель доступна по команде `/admin`
- [ ] Лицензия активна и проверена
- [ ] База данных создана и работает
- [ ] Логи записываются корректно
- [ ] Автозапуск настроен (systemd или Docker)
- [ ] Резервное копирование настроено
- [ ] Мониторинг работоспособности настроен
- [ ] Токен бота сохранен в безопасном месте
- [ ] Документация изучена

---

## 📞 Поддержка

Если вы столкнулись с проблемами:

1. Проверьте логи (`logs/bot.log`)
2. Изучите раздел "Решение проблем" выше
3. Проверьте документацию в `README.md`
4. Убедитесь, что все зависимости установлены
5. Проверьте правильность конфигурации в `.env`

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

**Важно:** Этот проект создан с нуля и не содержит кода из оригинального SoloBot. Все права защищены.

---

**🎉 Поздравляем! Ваш NexusBot успешно развернут и готов к работе!**
