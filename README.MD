# Blog REST API с кешированием

REST API для блога на FastAPI с поддержкой кеширования постов через Redis.

---

## Стек технологий

| Компонент | Технология |
|---|---|
| HTTP API | FastAPI |
| ORM | SQLAlchemy (async) |
| База данных | PostgreSQL |
| Кеш | Redis |
| Окружение | Docker Compose |
| Валидация | Pydantic |

---

## Архитектура

Приложение построено по слоистой архитектуре:

```
API (FastAPI routers)
        ↓
Service layer (бизнес-логика)
        ↓
Repository / DB layer (SQLAlchemy)
        ↓
PostgreSQL + Redis (кеш)
```

---

## Подход к кешированию

Используется стратегия **Cache-Aside (Lazy Loading)**.

### Алгоритм `GET /posts/{id}`

```
1. Проверяем Redis:
   cached_post = await redis.get(key)

2. Если найден → возвращаем из кеша

3. Если нет:
   - берём из PostgreSQL
   - кладём в Redis с TTL
   - возвращаем клиенту
```

### Инвалидация кеша

При `UPDATE` и `DELETE` ключ удаляется из Redis:

```python
await redis.delete(f"post:{post_id}")
```

### Почему Cache-Aside?

- Простота реализации
- Контроль над кешем на уровне приложения
- Нет лишней нагрузки при записи (в отличие от write-through)
- Подходит для read-heavy сценариев

---

## Эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/posts` | Создание поста |
| `GET` | `/posts` | Список постов |
| `GET` | `/posts/{id}` | Получение поста (с кешем) |
| `PATCH` | `/posts/{id}` | Обновление поста |
| `DELETE` | `/posts/{id}` | Удаление поста |

---

## Кеш

**Ключ:**
```
post:{id}
```

**TTL** задаётся через `.env`:
```env
POST_CACHE_TTL=300
```

**Сериализация:** `json.dumps(...)`

---

## Конфигурация

Все настройки вынесены в `.env`:

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=blog
DB_USER=postgres
DB_PASS=password

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redispassword
REDIS_DB=0

POST_CACHE_TTL=300
```

---

## Запуск

```bash
docker compose up --build
```

---

## Тестирование

```bash
pytest
```

### Что покрывают тесты

- Кеширование после первого запроса
- Возврат данных из кеша при повторном запросе
- Инвалидацию кеша при обновлении поста
- Инвалидацию кеша при удалении поста

### Инструменты

| Инструмент | Назначение |
|---|---|
| `pytest` | Фреймворк тестирования |
| `fakeredis` | Имитация Redis |
| SQLite in-memory | Тестовая БД |

---

## Обработка ошибок

- Пост не найден → `404 Not Found`
- Ошибки БД пробрасываются через сервисный слой
- Валидация входных данных — Pydantic

---

## База данных

- PostgreSQL в качестве основного хранилища
- Первичный ключ `id` индексирован автоматически
- Асинхронный доступ через SQLAlchemy
