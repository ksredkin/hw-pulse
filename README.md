# 🖥️ Hardware Pulse

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Sentry](https://img.shields.io/badge/Sentry-362D59?style=for-the-badge&logo=sentry&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-00A98F?style=for-the-badge&logo=alembic&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-FCC21B?style=for-the-badge&logo=ruff&logoColor=black)
![Mypy](https://img.shields.io/badge/mypy-checked-1f425f?style=for-the-badge)

## 📌 Описание

**Hardware Pulse** — это система для мониторинга состояния компьютеров и серверов через Telegram. 

Проект состоит из клиентского демона для сбора телеметрии, веб-API для приема метрик от множества устройств и Telegram-бота для просмотра статистики в реальном времени.

## 📊 Статистика и качество

🧪 Покрытие кода тестами: **74%**

🛠 **Качество кода:** проект проходит строгую проверку **Ruff** (линтинг/форматирование) и **Mypy** (статическая типизация)

🔄 **CI/CD:** Автоматическое тестирование и проверка типов при каждом Push (GitHub Actions)

🪰 **Мониторинг ошибок:** Интегрирован трекинг исключений **Sentry** (с раздельными DSN для API и Бота).

## 🧠 Компоненты системы
- 🕵️‍♂️ **Daemon (Клиент):** Легковесный фоновый фоновый скрипт на целевой машине. Собирает метрики (CPU, RAM, диски, сеть, температура), исполняет системные команды от сервера.
- ⚙️ **API (Сервер):** Принимает запросы от демонов, валидирует данные через Pydantic, управляет сессиями авторизации и распределяет команды.
- 🗄️ **БД и Кэш (Сервер):** PostgreSQL для долгосрочного хранения профилей (миграции Alembic) + Redis как высокоскоростной кэш метрик, хранилище локов авторизации и брокер сообщений (Pub/Sub).
- 🤖 **Telegram Bot (Сервер):** Асинхронный интерфейс на aiogram 3 с интерактивными инлайн-меню, поддержкой FSM для ввода настроек и Throttling Middleware против флуда.

## 🎯 Возможности
- 📊 **Сбор метрик:** Нагрузка на ядра CPU, использование RAM/Swap, заполненность дисков, сетевой трафик.
- 🌡️ **Контроль температуры:** Кроссплатформенный мониторинг нагрева процессора (включая Linux и Windows WMI).
- 🚨 **Мгновенные алерты:** Уведомления в Telegram при превышении заданного порога температуры на базе Redis Pub/Sub с умной блокировкой (Cooldown) от спама.
- 🎮 **Двустороннее управление (Remote Control):** Безопасная отправка системных команд (выключение, перезагрузка, сон) из чата бота на ПК по паттерну *Read-and-Delete*.
- 🔑 **Безопасность:** Генерация уникальных криптографических API-ключей для клиентов, защита эндпоинтов через FastAPI `Depends`.

## 📋 Требования

- 🔌 **Клиент:** Python 3.14+, Libre Hardware Monitor (только для ОС Windows)
- 🎛️ **Сервер:** Docker & Docker Compose, Telegram Bot Token (от [@BotFather](https://t.me/BotFather))

## ⚙️ Переменные окружения (`.env`)

Создайте файл `.env` в корне проекта по примеру ниже:

```env
# Daemon
DAEMON_API_HOST="http://<ваш_ip>:8000/metrics"
DAEMON_API_KEY="ваш_сгенерированный_ключ"

# API
API_HOST="0.0.0.0"
API_PORT=8000
API_SENTRY_DSN=

# Telegram bot
BOT_TOKEN="your_telegram_bot_token"
BOT_PROXY=
BOT_VLESS_PROXY=
BOT_SENTRY_DSN=

# Postgres
DB_HOST="hw-pulse-postgres"
DB_PORT=5432
DB_NAME="hw-pulse-db"
DB_USER="postgres"
DB_PASSWORD="123"
```

## 🚀 Запуск проекта
### 1. Серверная часть<br>
Запускается на сервере (Raspberry Pi, VPS) для обслуживания клиентов:

```Bash
git clone https://github.com/ksredkin/hw-pulse.git
cd hw-pulse
# Настройте .env файл
docker compose up --build -d
```

### 2. Клиентская часть (Daemon)
Запускается на машине, за которой необходимо следить:

1. Напишите боту команду /connect, чтобы зарегистрироваться и получить свой API_KEY.
2. Впишите полученный ключ и адрес сервера в ваш локальный файл .env.

**🖥️ Дополнительно для Windows (Мониторинг температуры):**
Для корректного сбора температуры процессора на Windows требуется утилита Libre Hardware Monitor:

Скачайте и запустите [Libre Hardware Monitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/download/v0.9.6/LibreHardwareMonitor.zip).

В верхнем меню программы включите следующие опции:

- Options ➔ Run On Windows Startup (автозапуск при старте ОС)

- Options ➔ Minimize To Tray (скрывать в трей при закрытии)

- Options ➔ Start Minimized (запускать сразу свернутым)

- Options ➔ Remote Web Server ➔ Run (активировать локальный веб-сервер)

После настройки запустите демона:

```Bash
poetry install --only main
poetry run python -m src.daemon
```

## 📌 Пример ответа бота

```Plaintext
🖥️ Статус системы:

🔥 CPU: 34.5% (Ядра: 6/12)
🌡️ Температура: 45.2°C
⚡ Частота: 3.8 GHz

🧠 Оперативная память (RAM):
Использовано: 45% (7.2 GB / 16.0 GB)
Доступно: 8.8 GB

💽 Диски:
C:\ - Занято: 70% (Свободно: 150 GB)
D:\ - Занято: 42% (Свободно: 580 GB)

🌐 Сеть:
Скачано: 1245 MB | Отправлено: 85 MB
```

## ⭐ Примечание
Если проект оказался полезным — можно поставить ⭐ на GitHub! 🚀