# REST API та OpenAPI

## 1. Загальний опис
API реалізоване на `FastAPI` і надає REST-інтерфейс для:
- автентифікації;
- керування користувачами;
- керування категоріями;
- роботи з оголошеннями;
- модерації;
- обміну повідомленнями;
- завантаження зображень.

Базова документація доступна через:
- `GET /docs` — Swagger UI;
- `GET /redoc` — ReDoc;
- `GET /openapi.json` — схема OpenAPI.

## 2. Ресурси API
### 2.1 Auth
- `POST /auth/register` — створити користувача
- `POST /auth/login` — отримати JWT

### 2.2 Users
- `GET /users/me` — поточний користувач
- `PATCH /users/me` — редагування власного профілю
- `GET /users` — список користувачів (admin)
- `GET /users/{user_id}` — користувач за id (admin)
- `PATCH /users/{user_id}` — зміна користувача (admin)
- `DELETE /users/{user_id}` — видалення користувача (admin)

### 2.3 Categories
- `POST /categories` — створення категорії
- `GET /categories` — список категорій
- `GET /categories/{category_id}` — одна категорія
- `PUT /categories/{category_id}` — редагування категорії
- `DELETE /categories/{category_id}` — видалення категорії

### 2.4 Listings
- `POST /listings` — створення оголошення
- `PUT /listings/{listing_id}` — редагування
- `GET /listings` — публічний каталог
- `GET /listings/me/owned` — власні оголошення
- `GET /listings/moderation/pending` — черга модерації
- `GET /listings/{listing_id}` — детальна сторінка
- `DELETE /listings/{listing_id}` — архівація / видалення з боку власника

### 2.5 Moderation
- `POST /moderation/listings/{listing_id}` — схвалення або відхилення оголошення

### 2.6 Messages
- `POST /messages` — надсилання повідомлення
- `GET /messages/me` — список власних повідомлень
- `GET /messages/{message_id}` — одне повідомлення
- `DELETE /messages/{message_id}` — видалення повідомлення

### 2.7 Uploads
- `POST /uploads/images` — завантаження зображень

### 2.8 Health
- `GET /health` — технічний healthcheck

## 3. Модель автентифікації
Захищені маршрути використовують:
- заголовок `Authorization`
- формат: `Bearer <JWT_TOKEN>`

JWT формується на основі email користувача і має час життя, керований конфігурацією:
- `APP_ACCESS_TOKEN_EXPIRE_MINUTES`

## 4. Основні DTO
### Auth DTO
- `UserCreateDTO`
- `UserLoginDTO`
- `TokenDTO`

### User DTO
- `UserReadDTO`
- `UserUpdateDTO`
- `UserAdminUpdateDTO`

### Category DTO
- `CategoryCreateDTO`
- `CategoryUpdateDTO`
- `CategoryReadDTO`

### Listing DTO
- `ListingCreateDTO`
- `ListingUpdateDTO`
- `ListingReadDTO`
- `UploadImageReadDTO`
- `UploadImageBatchDTO`

### Message DTO
- `MessageCreateDTO`
- `MessageReadDTO`

### Moderation DTO
- `ModerationDecisionDTO`

### Utility DTO
- `DeleteResponseDTO`

## 5. HTTP статус-коди
- `200 OK` — успішне читання, редагування або видалення
- `201 Created` — успішне створення ресурсу
- `400 Bad Request` — невалідний сценарій або payload
- `401 Unauthorized` — відсутній або невалідний токен
- `403 Forbidden` — недостатньо прав
- `404 Not Found` — ресурс не знайдено
- `409 Conflict` — дублювання або конфлікт стану

## 6. Пошук і фільтрація каталогу
`GET /listings` підтримує:
- `query`
- `category_id`
- `min_price`
- `max_price`
- `sort_by=created_at|price`
- `sort_order=asc|desc`

## 7. Життєвий цикл оголошення
1. Користувач створює оголошення.
2. Оголошення отримує статус `pending`.
3. Модератор:
   - або схвалює його -> `approved`
   - або відхиляє -> `rejected`
4. Власник може редагувати або архівувати оголошення.

## 8. Upload API
`POST /uploads/images`:
- приймає список `UploadFile`;
- обмежує кількість файлів;
- перевіряє MIME-тип;
- перевіряє порожній файл;
- перевіряє обмеження розміру;
- повертає список URL, які можна одразу вставляти в `ListingCreateDTO`.

## 9. Приклади ключових сценаріїв
### Реєстрація
`POST /auth/register`
```json
{
  "email": "seller@example.com",
  "full_name": "Test Seller",
  "password": "Admin123!"
}
```

### Логін
`POST /auth/login`
```json
{
  "email": "seller@example.com",
  "password": "Admin123!"
}
```

### Створення оголошення
`POST /listings`
```json
{
  "title": "MacBook Pro 14 M3",
  "description": "Ноутбук у відмінному стані, повний комплект, мінімальні сліди використання.",
  "price": 1799.0,
  "category_id": 1,
  "image_urls": [
    "/demo-images/macbook-pro-14-m3.svg"
  ]
}
```

### Модерація
`POST /moderation/listings/{listing_id}`
```json
{
  "approved": false,
  "reason": "Опис не містить достатньо інформації про стан товару."
}
```

## 10. Відповідність frontend
Frontend інтегрується з API через:
- авторизацію токеном;
- `workspace` для приватних дій;
- `catalog` для публічного читання;
- `listing detail` для перегляду окремого оголошення;
- `uploads` для завантаження зображень у процесі публікації.
