# Тестування

## Підхід
- `unit` тести перевіряють сервіси, security helpers, DTO validation та database bootstrap.
- `integration` тести перевіряють REST API, auth, moderation, listings, categories, users і messages.
- окремі `mongodb-smoke` сценарії перевіряють bootstrap Mongo-підходу та numeric counters.

## Інструменти
- `pytest`
- `pytest-cov`
- `httpx`
- `mongomock`

## Обсяг
- локально збирається понад `200` тест-кейсів;
- параметризовані матриці покривають edge cases для DTO, auth та role-based access;
- локальний прогін `pytest -q` проходить повністю.

## Звіти
Тестовий pipeline генерує:
- `pytest-report.xml`
- `coverage.xml`
- `htmlcov/`

Ці файли використовуються для:
- SonarQube / SonarCloud import
- CI artifacts download
- локального аналізу непокритих рядків

## Поточний фокус покриття
- реєстрація та логін
- CRUD категорій
- життєвий цикл оголошення
- модерація
- повідомлення
- права доступу
- DTO validation / bad input cases
- security helpers / token-password flows
