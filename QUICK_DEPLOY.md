# NexusBot - Быстрое развертывание одной командой

## 🚀 Мгновенный запуск

### Одна команда для полного развертывания:

```bash
./deploy.sh
```

Или с указанием команды явно:

```bash
./deploy.sh deploy
```

## 📋 Что делает скрипт?

При запуске `./deploy.sh` автоматически:

1. ✅ **Проверяет требования** - Docker и Docker Compose
2. ✅ **Создает директорию** - config, data, logs, licenses
3. ✅ **Генерирует .env файл** - с настройками по умолчанию
4. ✅ **Создает конфиги** - файлы конфигурации
5. ✅ **Собирает Docker образ** - nexusbot:latest
6. ✅ **Запускает контейнер** - в фоновом режиме
7. ✅ **Показывает статус** - проверка работоспособности

## 🔧 Все команды скрипта

| Команда | Описание |
|---------|----------|
| `./deploy.sh` или `./deploy.sh deploy` | Полное развертывание |
| `./deploy.sh start` | Запустить бота |
| `./deploy.sh stop` | Остановить бота |
| `./deploy.sh restart` | Перезапустить бота |
| `./deploy.sh logs` | Просмотр логов в реальном времени |
| `./deploy.sh status` | Показать статус контейнера |
| `./deploy.sh update` | Обновить бота до последней версии |
| `./deploy.sh backup` | Создать резервную копию данных |
| `./deploy.sh clean` | Удалить всё (контейнеры, данные, образы) |
| `./deploy.sh help` | Показать справку |

## 📝 Пошаговая инструкция

### Шаг 1: Запуск скрипта

```bash
chmod +x deploy.sh
./deploy.sh
```

### Шаг 2: Настройка токена

После запуска отредактируйте файл `.env`:

```bash
nano .env
```

Укажите ваш токен от @BotFather:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Шаг 3: Перезапуск с настройками

```bash
./deploy.sh restart
```

### Шаг 4: Проверка логов

```bash
./deploy.sh logs
```

## 🐳 Ручное управление через Docker Compose

Если предпочитаете использовать Docker Compose напрямую:

```bash
# Сборка и запуск
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление
docker-compose pull
docker-compose up -d
```

## ⚙️ Переменные окружения (.env)

| Переменная | Описание | Пример |
|------------|----------|--------|
| `BOT_TOKEN` | Токен Telegram бота | `123456:ABCdef...` |
| `ADMIN_IDS` | ID администраторов (через запятую) | `123456789,987654321` |
| `LICENSE_CHECK_ENABLED` | Проверка лицензии | `false` |
| `DATABASE_URL` | URL базы данных | `sqlite:///data/nexusbot.db` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `TZ` | Часовой пояс | `Europe/Moscow` |
| `WEBHOOK_URL` | URL вебхука (опционально) | `https://yourdomain.com/webhook` |
| `REDIS_URL` | Redis для кэша (опционально) | `redis://localhost:6379` |

## 📁 Структура после развертывания

```
nexusbot/
├── .env                 # Конфигурация (создается скриптом)
├── deploy.sh            # Скрипт развертывания
├── docker-compose.yml   # Docker Compose конфигурация
├── Dockerfile           # Docker образ
├── config/              # Файлы конфигурации
├── data/                # База данных и файлы
├── logs/                # Логи бота
└── licenses/            # Лицензионные ключи (если включено)
```

## 🔒 Безопасность

- ✅ Контейнер запускается от непривилегированного пользователя
- ✅ Томы монтируются только для необходимых директорий
- ✅ Нет доступа к хост-системе
- ✅ Лимитированный размер логов (10MB, 3 файла)
- ✅ Health check для мониторинга состояния

## 💾 Резервное копирование

### Автоматически:

```bash
./deploy.sh backup
```

### Вручную:

```bash
# Создать директорию для бэкапа
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# Скопировать данные
cp -r data/ backups/$(date +%Y%m%d_%H%M%S)/
cp -r config/ backups/$(date +%Y%m%d_%H%M%S)/
cp .env backups/$(date +%Y%m%d_%H%M%S)/
```

## 🔄 Обновление

### Через скрипт:

```bash
./deploy.sh update
```

### Вручную:

```bash
git pull
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

## 🆘 Решение проблем

### Бот не запускается

1. Проверьте токен в `.env`
2. Посмотрите логи: `./deploy.sh logs`
3. Проверьте статус: `./deploy.sh status`

### Ошибка Docker

```bash
# Пересобрать образ
docker-compose build --no-cache

# Очистить кэш Docker
docker system prune -a
```

### Проблемы с правами

```bash
# Исправить права на директорию
sudo chown -R $USER:$USER data logs config licenses
```

### Полный сброс

```bash
# Удалить всё и начать заново
./deploy.sh clean
./deploy.sh
```

## 📊 Мониторинг

### Статус контейнера:

```bash
docker stats nexusbot
```

### Использование ресурсов:

```bash
docker inspect nexusbot
```

### Логи в реальном времени:

```bash
./deploy.sh logs
```

## 🎯 Примеры использования

### Быстрый старт для тестирования:

```bash
./deploy.sh
# Отредактировать .env
./deploy.sh restart
./deploy.sh logs
```

### Развертывание на продакшене:

```bash
# Настроить переменные окружения
export BOT_TOKEN="your_token"
export ADMIN_IDS="your_admin_id"

# Запустить
./deploy.sh

# Создать бэкап
./deploy.sh backup
```

### Обновление на продакшене:

```bash
# Создать бэкап
./deploy.sh backup

# Обновить
./deploy.sh update

# Проверить логи
./deploy.sh logs
```

## 📞 Поддержка

- Документация: `README.md`, `DEPLOYMENT.md`, `INSTALL.md`
- GitHub: https://github.com/yourusername/nexusbot
- Лицензия: MIT (свободное использование)

---

**NexusBot** - Свободный Telegram бот с открытым исходным кодом  
Лицензия: MIT - разрешено коммерческое использование
