# 🖥️ Hardware Pulse

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
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

🧪 Покрытие кода тестами: **46%**

🛠 **Качество кода:** проект проходит строгую проверку **Ruff** (линтинг/форматирование) и **Mypy** (статическая типизация)

🔄 **CI/CD:** Автоматическое тестирование и проверка типов при каждом Push (GitHub Actions)

## 🧠 Компоненты системы

- 🕵️‍♂️ **Daemon (Клиент):** Легковесный скрипт на целевой машине. Собирает метрики (CPU, RAM, диски, сеть, температура) и отправляет их по HTTP.
- ⚙️ **API (Сервер):** Принимает запросы на FastAPI, валидирует данные через Pydantic и проверяет API-ключи.
- 🗄️ **БД и Кэш (Сервер):** PostgreSQL для хранения пользователей (миграции Alembic) + Redis для кэширования метрик и сессий авторизации.
- 🤖 **Telegram Bot (Сервер):** Асинхронный интерфейс на aiogram 3 для управления и вывода статистики.

## 🎯 Возможности
- 📊 Сбор метрик: нагрузка на ядра CPU, использование RAM и Swap, заполненность дисков, сетевой трафик.
- 🌡️ Кроссплатформенный мониторинг температуры (включая Linux и Windows WMI).
- 🔑 Многопользовательский режим: генерация уникальных криптографических API-ключей для клиентов.
- 🛡️ Защита API-эндпоинтов зависимостями авторизации (`Depends`).
- 🔄 Автоматическое применение миграций базы данных при старте серверной части.

## 📋 Требования

- 🔌 **Клиент:** Python 3.14+ (для работы демона), Libre Hardware Monitor (для Windows)
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

# Telegram bot
BOT_TOKEN="your_telegram_bot_token"
BOT_PROXY=
BOT_VLESS_PROXY=

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