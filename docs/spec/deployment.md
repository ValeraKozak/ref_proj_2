# Розгортання

## Локально
1. Створити `.env` на основі `.env.example`
2. Запустити MongoDB локально або через Docker
3. Підняти API:
   `uvicorn src.main:app --reload`
4. Підняти frontend:
   `cd frontend && npm run dev`

## Docker Compose
```powershell
docker compose up --build
```

Stack:
- `db` — MongoDB
- `api` — FastAPI
- `frontend` — production build через `nginx`

## CI/CD
Pipeline виконує:
- lint (`ruff`)
- unit + integration tests
- coverage XML + HTML reports
- upload CI artifacts
- умовний SonarQube / SonarCloud scan
- Sonar Quality Gate check, якщо налаштовані secrets

Artifacts після коміту:
- `coverage.xml`
- `pytest-report.xml`
- `ruff-report.txt`
- `htmlcov/`

## Sonar Secrets
Для активації Sonar у GitHub Actions потрібні:
- `SONAR_TOKEN`
- `SONAR_HOST_URL`

Для SonarCloud:
```text
SONAR_HOST_URL=https://sonarcloud.io
```

## Змінні середовища
Основна змінна:
```env
APP_DATABASE_URL=mongodb://db:27017/bulletin_board
```
