# Розгортання та DevOps

## 1. Локальний запуск
### Кроки
1. Створити `.env` на основі [`.env.example`](../../.env.example)
2. Підняти MongoDB локально або через Docker
3. Запустити backend:
   ```powershell
   uvicorn src.main:app --reload
   ```
4. Запустити frontend:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

## 2. Docker Compose
Для повного стеку використовується:
```powershell
docker compose up --build
```

Stack:
- `db` — MongoDB
- `api` — FastAPI
- `frontend` — production build через `nginx`

## 3. Ключові змінні середовища
### Backend
- `APP_APP_NAME`
- `APP_APP_ENV`
- `APP_DATABASE_URL`
- `APP_SECRET_KEY`
- `APP_ACCESS_TOKEN_EXPIRE_MINUTES`
- `APP_ALGORITHM`
- `APP_LOG_LEVEL`

### Приклад
```env
APP_DATABASE_URL=mongodb://db:27017/bulletin_board
APP_SECRET_KEY=CHANGE_ME_WITH_A_RANDOM_VALUE
```

## 4. CI/CD Pipeline
Workflow [ci.yml](../../.github/workflows/ci.yml) виконує:
- checkout коду;
- встановлення залежностей;
- запуск `ruff`;
- запуск unit та integration тестів;
- генерацію `coverage.xml`, `pytest-report.xml`, `htmlcov/`;
- upload artifacts;
- запуск SonarCloud scan;
- перевірку Sonar Quality Gate.

Окремо workflow [deploy.yml](../../.github/workflows/deploy.yml) відповідає за збірку й публікацію контейнерного image.

## 5. Артефакти збірки
Після кожного коміту CI зберігає:
- `coverage.xml`
- `pytest-report.xml`
- `ruff-report.txt`
- `htmlcov/`

Ці файли доступні для завантаження з GitHub Actions run.

## 6. SonarCloud
Для SonarCloud у репозиторії використовується:
- [sonar-project.properties](../../sonar-project.properties)
- `SONAR_TOKEN` як GitHub secret

`SONAR_HOST_URL` у workflow зафіксований як:
```text
https://sonarcloud.io
```

## 7. Гілки та merge policy
Рекомендований порядок:
1. створити feature branch;
2. відкрити Pull Request;
3. дочекатися зелених checks;
4. переконатися, що Quality Gate пройдено;
5. тільки після цього merge у `main`.

## 8. Branch Protection
У GitHub Settings бажано увімкнути:
- required status check для `CI`
- required status check для `CD` за потреби
- required status check для SonarCloud code analysis / quality gate
- заборону merge при невдалих checks

## 9. Локальна перевірка перед push
Рекомендований мінімальний набір:
```powershell
py -m ruff check src tests
py -m pytest -q -p no:cacheprovider
```

За потреби:
```powershell
py -m pytest --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=html:htmlcov --junitxml=pytest-report.xml -q -p no:cacheprovider
```

## 10. Операційні нотатки
- demo-дані не повинні змінюватися без окремого запиту;
- uploads директорія ігнорується Git;
- CI використовує `mongomock` для ізольованих тестів;
- Sonar coverage розраховується для backend-шару, для якого реально генерується coverage report.
