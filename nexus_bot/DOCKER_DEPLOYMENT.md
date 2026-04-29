# 🐳 Docker Deployment Guide для NexusBot

## 📋 Обзор

Проект полностью готов к развертыванию в Docker. Все зависимости включены в контейнер, база данных PostgreSQL и мониторинг Prometheus/Grafana настроены через `docker-compose.yml`.

---

## 🚀 Быстрый старт

### Вариант 1: SQLite (для тестирования)

```bash
# 1. Клонируйте репозиторий
cd nexus_bot

# 2. Скопируйте шаблон конфигурации
cp .env.example .env

# 3. Отредактируйте .env - укажите хотя бы BOT_TOKEN и BOT_ADMIN_IDS
nano .env

# 4. Запустите только бота с SQLite
docker-compose up -d nexusbot

# 5. Проверьте логи
docker-compose logs -f nexusbot
```

### Вариант 2: Полный стек с PostgreSQL и мониторингом (продакшен)

```bash
# 1. Клонируйте репозиторий
cd nexus_bot

# 2. Скопируйте шаблон конфигурации
cp .env.example .env

# 3. Отредактируйте .env
nano .env
```

**Обязательные настройки в `.env`:**
```ini
BOT_TOKEN=your_real_token_from_BotFather
BOT_ADMIN_IDS=your_telegram_id

# Для PostgreSQL:
DATABASE_URL=postgresql+asyncpg://nexusbot:secure_password_change_me@db:5432/nexusbot
POSTGRES_USER=nexusbot
POSTGRES_PASSWORD=secure_password_change_me
POSTGRES_DB=nexusbot

# Опционально включить мониторинг:
PROMETHEUS_ENABLED=true
```

```bash
# 4. Запустите весь стек
docker-compose up -d

# 5. Проверьте статус
docker-compose ps

# 6. Просмотр логов
docker-compose logs -f nexusbot
```

---

## 📦 Компоненты стека

| Сервис | Порт | Описание |
|--------|------|----------|
| **nexusbot** | 9090 | Основной бот (метрики Prometheus) |
| **db** (PostgreSQL) | 5432 | База данных (по умолчанию закрыт) |
| **prometheus** | 9091 | Сбор метрик (по умолчанию закрыт) |
| **grafana** | 3000 | Визуализация метрик (по умолчанию закрыт) |

> ⚠️ Порты закрыты по умолчанию для безопасности. Раскомментируйте в `docker-compose.yml` если нужен внешний доступ.

---

## 🔧 Управление

### Запуск
```bash
# Запустить все сервисы
docker-compose up -d

# Запустить только бота
docker-compose up -d nexusbot

# Запустить бота и базу данных
docker-compose up -d nexusbot db
```

### Остановка
```bash
# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (данные будут потеряны!)
docker-compose down -v
```

### Перезапуск
```bash
# Перезапустить бота
docker-compose restart nexusbot

# Пересобрать и запустить
docker-compose up -d --build
```

### Логи
```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f nexusbot
docker-compose logs -f db
```

### Мониторинг состояния
```bash
# Статус сервисов
docker-compose ps

# Использование ресурсов
docker stats
```

---

## 💾 Сохранение данных

Данные сохраняются в Docker volumes:

- `nexusbot_data` - SQLite база данных (если используется)
- `postgres_data` - PostgreSQL база данных
- `nexusbot_logs` - Логи бота
- `prometheus_data` - Данные метрик Prometheus
- `grafana_data` - Настройки Grafana

**Для backup:**
```bash
# Backup PostgreSQL
docker exec nexusbot_db pg_dump -U nexusbot nexusbot > backup.sql

# Restore PostgreSQL
docker exec -i nexusbot_db psql -U nexusbot nexusbot < backup.sql

# Backup volume с базой данных
docker run --rm -v nexusbot_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

---

## 🔐 Безопасность

### Обязательно измените в `.env`:
1. `BOT_TOKEN` - получите от @BotFather
2. `BOT_ADMIN_IDS` - узнайте свой ID через @userinfobot
3. `POSTGRES_PASSWORD` - используйте сложный пароль
4. `GRAFANA_ADMIN_PASSWORD` - смените пароль по умолчанию

### Рекомендации:
- Не публикуйте `.env` файл в репозиторий
- Используйте secrets для продакшена
- Закройте порты БД и мониторинга (раскомментированы по умолчанию)
- Регулярно обновляйте образы: `docker-compose pull && docker-compose up -d`

---

## 📊 Мониторинг

### Включить Prometheus и Grafana:

1. В `.env` установите:
   ```ini
   PROMETHEUS_ENABLED=true
   ```

2. Раскомментируйте порты в `docker-compose.yml`:
   ```yaml
   # prometheus:
   ports:
     - "9091:9090"
   
   # grafana:
   ports:
     - "3000:3000"
   ```

3. Перезапустите:
   ```bash
   docker-compose up -d
   ```

4. Откройте в браузере:
   - **Prometheus**: http://localhost:9091
   - **Grafana**: http://localhost:3000 (admin/admin)

5. В Grafana добавьте datasource Prometheus:
   - URL: `http://prometheus:9090`

---

## 🛠️ Troubleshooting

### Бот не запускается
```bash
# Проверьте логи
docker-compose logs nexusbot

# Убедитесь что токен правильный
docker-compose exec nexusbot env | grep BOT_TOKEN
```

### Ошибка подключения к базе данных
```bash
# Проверьте что БД запущена
docker-compose ps db

# Проверьте логи БД
docker-compose logs db

# Проверьте переменную DATABASE_URL
docker-compose exec nexusbot env | grep DATABASE_URL
```

### Prometheus не собирает метрики
```bash
# Проверьте что PROMETHEUS_ENABLED=true
docker-compose exec nexusbot env | grep PROMETHEUS

# Проверьте конфиг Prometheus
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
```

### Сбросить всё и начать заново
```bash
# Остановить и удалить всё
docker-compose down -v

# Удалить образы
docker-compose rm -f

# Запустить заново
docker-compose up -d --build
```

---

## 📈 Обновление

```bash
# Обновить образы
docker-compose pull

# Пересобрать и перезапустить
docker-compose up -d --build

# Очистить старые образы
docker image prune -f
```

---

## 🎯 Production Checklist

- [ ] Изменен `BOT_TOKEN` на реальный
- [ ] Указаны реальные `BOT_ADMIN_IDS`
- [ ] Изменен пароль PostgreSQL (`POSTGRES_PASSWORD`)
- [ ] Изменен пароль Grafana (`GRAFANA_ADMIN_PASSWORD`)
- [ ] Включен Prometheus (опционально)
- [ ] Настроен backup базы данных
- [ ] Настроено логирование
- [ ] Закрыты ненужные порты
- [ ] Настроен мониторинг и алерты

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Убедитесь что все переменные окружения настроены
3. Проверьте состояние контейнеров: `docker-compose ps`
4. Обратитесь в @nexus_support
