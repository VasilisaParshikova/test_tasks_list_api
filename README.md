# Описание
API для системы управления списком задач с аутентификацией через Bearer-токен.



### Стек
- Python 3.11
- FastAPI
- PostgreSQL
- Redis
- Docker
- SQLAlchemy (asyncpg)

полный список зависимостей указан в файле requirements.txt

# Установка
### Склонировать репозиторий

- `git clone https://github.com/VasilisaParshikova/test_tasks_list_api`

### Настройка окружения

- Установить Docker
- Создайте secret key для JWT (команда: openssl rand -hex 32)
- Сформируйте файл переменных окружения, согласно .env.example

### Запуск

- docker-compose up -d

### Документация

- После запуска приложения документация к api будет доступна по ссылке {your_domain}/docs
