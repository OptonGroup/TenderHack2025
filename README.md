# TenderHack2025 - ИИ-ассистент для портала закупок Москвы

🚀 TenderHack 2025

## 📋 Описание

TenderHack 2025 - это современная платформа для организации тендеров и закупок, с интегрированным AI-ассистентом для поддержки пользователей. Система включает функционал регистрации и авторизации, а также AI-чат с возможностью эскалации запросов к живым операторам.

## 🔧 Интересные технические решения

- ✨ **Двухфакторная аутентификация** с использованием access и refresh токенов, хранящихся в [HTTP-only cookies](https://developer.mozilla.org/ru/docs/Web/HTTP/Cookies)
- 🔐 **CSRF-защита**
- 🤖 **AI-интеграция** с локальной моделью [Microsoft Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/phi-3-mini-4k-instruct)
- 📈 **Асинхронное API** с использованием [FastAPI](https://fastapi.tiangolo.com/)
- 📄 **Валидация данных** через [Pydantic](https://docs.pydantic.dev/)
- 📱 **Адаптивный интерфейс**

## 📚 Используемые технологии и библиотеки

- [FastAPI](https://fastapi.tiangolo.com/) - современный высокопроизводительный веб-фреймворк
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL тулкит и ORM
- [JWT](https://jwt.io/) - безопасный механизм передачи данных в формате JSON
- [Pydantic](https://docs.pydantic.dev/) - библиотека для валидации данных
- [Jinja2](https://jinja.palletsprojects.com/) - шаблонизатор для Python
- [pandas](https://pandas.pydata.org/) - библиотека для анализа данных
- [uvicorn](https://www.uvicorn.org/) - ASGI сервер для Python
- [Passlib](https://passlib.readthedocs.io/) - библиотека для хэширования паролей
- [Microsoft Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/phi-3-mini-4k-instruct) - языковая модель для локального развертывания

## 📂 Структура проекта

```
TenderHack2025/
├── Backend/
│   ├── static/
│   │   ├── js/
│   │   ├── css/
│   │   └── img/
│   ├── templates/
│   ├── uploads/
│   │   └── tenders/
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── server.py
├── Neyro/
│   ├── tests/
│   ├── analyze/
│   ├── app.py
│   ├── model.py
│   ├── utils.py
│   ├── requirements.txt
│   └── dictionary_ru.txt
├── docs/
│   └── dataset.parquet
└── README.md
```

- **Backend/** - основная директория с кодом приложения
  - **static/** - статические файлы (JavaScript, CSS, изображения)
  - **templates/** - шаблоны Jinja2 для рендеринга HTML
  - **uploads/** - директория для загружаемых пользователями файлов
- **Neyro/** - модуль для работы с моделью Microsoft Phi-3
  - **tests/** - юнит-тесты для моделей и утилит
  - **analyze/** - скрипты для анализа производительности моделей
  - **model.py** - основная реализация работы с LLM-моделью
  - **utils.py** - вспомогательные функции для обработки и нормализации текста
  - **dictionary_ru.txt** - словарь русских слов для проверки правописания

## 💡 Особенности реализации

- 🛡️ Защита от CSRF-атак
- 📝 Хэширование паролей с использованием алгоритма bcrypt
- 🗄️ Использование ORM SQLAlchemy для работы с базой данных
- 🤖 AI-чат с возможностью эскалации к оператору поддержки
- 📊 Административная панель для управления пользователями и мониторинга системы

## 🔌 API Эндпоинты для работы с пользователями и чатами

### Пользователи (Users)

- 🔐 **POST /api/login** - Аутентификация пользователя с выдачей JWT токенов
- 📝 **POST /api/register** - Регистрация нового пользователя
- 🔑 **POST /api/refresh-token** - Обновление access токена с помощью refresh токена
- 🚪 **POST /api/logout** - Выход из системы, инвалидация токенов
- 👤 **GET /api/users/me** - Получение информации о текущем пользователе
- 📋 **GET /api/users** - Получение списка всех пользователей (admin)
- 🔍 **GET /api/users/{user_id}** - Получение информации о пользователе по ID

### Чаты (Chat)

- 💬 **POST /api/chat-history** - Создание нового сообщения в чате
- 📚 **GET /api/chat-history** - Получение истории чатов пользователя
- 📖 **GET /api/chat-history/{chat_id}** - Получение конкретного чата по ID
- ✏️ **PATCH /api/chat-history/{message_id}** - Обновление сообщения
- 🗑️ **DELETE /api/chat-history/{chat_id}** - Удаление чата
- ⭐ **POST /api/chat-history/{chat_id}/finish** - Завершение чата с рейтингом
- 👨‍💼 **POST /api/call-operator** - Запрос на подключение оператора поддержки
- 📊 **GET /api/support-requests** - Получение запросов в поддержку (для операторов)
- ✅ **POST /api/support-requests/{chat_id}/resolve** - Разрешение запроса поддержки

## 🚀 Запуск проекта

### Локальная установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/TenderHack2025.git
cd TenderHack2025

# Установка зависимостей Backend
pip install -r requirements.txt

# Установка зависимостей Neyro
cd Neyro
pip install -r requirements.txt
cd ..

# Запуск сервера
cd Backend
uvicorn server:app --reload
```

### Запуск через Docker

```bash
# Сборка образа
docker build -t tenderhack2025 .

# Запуск контейнера
docker run -d -p 8000:8000 --name tenderhack tenderhack2025
```

Или с помощью Docker Compose:

```bash
# Запуск с помощью docker-compose
docker-compose up -d
```

## 🧠 Модуль Neyro

Модуль `Neyro` представляет собой серверную часть AI-ассистента, основанного на модели **Microsoft Phi-3-mini-4k-instruct**. Особенности:

- 🌐 Локальное развертывание нейросети без зависимости от внешних API
- ⚡ Оптимизация для работы на CPU с минимальными требованиями к ресурсам
- 🇷🇺 Полноценная поддержка русского языка с использованием словаря
- 📏 Контекстная обработка и анализ текстов до 4000 токенов
- 🔄 Автоматическое определение необходимости эскалации к оператору
- 📊 Встроенные механизмы анализа и стресс-тестирования модели

Файл [`model.py`](./Neyro/model.py) содержит основные классы для работы с моделью, а [`utils.py`](./Neyro/utils.py) предоставляет набор утилит для предобработки текста и оптимизации скорости работы.

Запуск модуля Neyro отдельно:

```bash
cd Neyro
python app.py
```

## 🏗️ Сборка проекта

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r Neyro/requirements.txt

# Инициализация базы данных
python -c "from Backend.database import init_db; init_db()"

# Сборка фронтенда (если используется npm)
cd Frontend
npm install
npm run build
cd ..

# Упаковка в Docker (опционально)
docker build -t tenderhack2025 
```
