# Domain Model

## 1. Основні сутності
### User
Описує обліковий запис користувача платформи.

Атрибути:
- `id`
- `email`
- `full_name`
- `password_hash`
- `role`
- `is_blocked`
- `created_at`

### Category
Описує категорію каталогу.

Атрибути:
- `id`
- `name`
- `description`

### Listing
Описує оголошення користувача.

Атрибути:
- `id`
- `title`
- `description`
- `price`
- `status`
- `rejection_reason`
- `owner_id`
- `category_id`
- `created_at`
- `updated_at`

### ListingImage
Описує зображення, прив’язане до оголошення.

Атрибути:
- `id`
- `listing_id`
- `url`
- `position`

### Message
Описує повідомлення між користувачами в контексті оголошення.

Атрибути:
- `id`
- `listing_id`
- `sender_id`
- `recipient_id`
- `body`
- `created_at`

## 2. Зв’язки
- `User` 1..* `Listing`
- `Category` 1..* `Listing`
- `Listing` 1..* `ListingImage`
- `Listing` 1..* `Message`
- `User` 1..* `Message` як `sender`
- `User` 1..* `Message` як `recipient`

## 3. Доменно важливі стани
### Role
- `user`
- `moderator`
- `admin`

### ListingStatus
- `draft`
- `pending`
- `approved`
- `rejected`
- `archived`

## 4. Бізнес-правила домену
- заблокований користувач не може створювати нові оголошення;
- нове оголошення не потрапляє в публічний каталог без схвалення;
- категорія не може бути безконтрольно видалена, якщо на неї є посилання;
- повідомлення дозволені тільки в контексті оголошення;
- модерація змінює видимість оголошення в каталозі.
