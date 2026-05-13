# Тестування

## Підхід
- `unit` тести перевіряють сервіси, security helpers, DTO validation та архітектурні патерни;
- `integration` тести перевіряють REST API, auth, moderation, listings, categories, users і messages;
- окремі `mongodb-smoke` сценарії перевіряють bootstrap Mongo-підходу та numeric counters.

## Інструменти
- `pytest`
- `pytest-cov`
- `httpx`
- `mongomock`

## Обсяг
- локально збирається понад `200` тест-кейсів;
- параметризовані матриці покривають edge cases для DTO, auth і role-based access;
- локальний прогін `pytest -q` має проходити повністю перед комітом.

## Звіти
Тестовий pipeline генерує:
- `pytest-report.xml`
- `coverage.xml`
- `htmlcov/`

Ці файли використовуються для:
- SonarQube / SonarCloud import;
- CI artifact downloads;
- локального аналізу непокритих рядків і регресій.

## Поточний фокус покриття
- реєстрація та логін;
- CRUD категорій;
- життєвий цикл оголошення;
- модерація;
- повідомлення;
- права доступу;
- DTO validation / bad input cases;
- security helpers / token-password flows;
- архітектурні утиліти для strategy/factory шару.
