# Bulletin Board Platform

![CI](https://github.com/ValeraKozak/ref_proj_2/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/ValeraKozak/ref_proj_2/actions/workflows/deploy.yml/badge.svg)
![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=ValeraKozak_ref_proj_2&metric=alert_status)
![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ValeraKozak_ref_proj_2&metric=coverage)

Educational marketplace project built with `FastAPI`, `MongoDB`, and a React frontend. The platform supports listings, categories, moderation, messaging, image uploads, and a catalog/detail experience for bulletin-board style publishing.

## Highlights
- JWT registration and login
- Roles: `user`, `moderator`, `admin`
- Listing lifecycle: create, edit, moderate, archive
- Categories and moderation workspace
- Catalog search, filters, sorting, and detail page
- Messaging between buyers and sellers
- Image upload endpoint and static upload serving
- Unit and integration tests with coverage reporting
- Dockerized local run and GitHub Actions CI/CD

## Stack
- Python 3.11
- FastAPI
- MongoDB / PyMongo
- Pydantic v2
- React + Vite
- Pytest + pytest-cov + mongomock
- Docker
- GitHub Actions
- SonarQube / SonarCloud ready pipeline

## Repository Structure
```text
src/
  controllers/
  services/
  repositories/
  models/
  dto/
  db/
  utils/
tests/
  unit/
  integration/
docs/
  diagrams/
  spec/
.cursor/
  rules/
.github/workflows/
frontend/
```

## Local Backend Run
```powershell
py -m venv .venv
. .venv\Scripts\Activate.ps1
py -m pip install -e .[dev]
Copy-Item .env.example .env
uvicorn src.main:app --reload
```

Example local database URL:
```env
APP_DATABASE_URL=mongodb://localhost:27017/bulletin_board
```

Swagger:
- `http://127.0.0.1:8000/docs`

## Local Frontend Run
```powershell
cd frontend
npm install
npm run dev
```

## One-command Local Run
```powershell
.\run.ps1
```

## Docker Run
```powershell
Copy-Item .env.example .env
docker compose up --build
```

Available services:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:5173`
- MongoDB: `mongodb://localhost:27017`

## Testing and Reports
Run tests with XML and HTML coverage output:
```powershell
py -m pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html --junitxml=pytest-report.xml
```

Generated outputs:
- `coverage.xml`
- `pytest-report.xml`
- `htmlcov/`

CI uploads these artifacts after every commit so they can be downloaded from the workflow run.

## SonarQube / SonarCloud
The repository includes:
- `sonar-project.properties`
- XML coverage and test reports for scanner import
- conditional Sonar scan and Quality Gate steps in CI

To enable Sonar in GitHub Actions, configure:
- `SONAR_TOKEN`
- `SONAR_HOST_URL`

If you use SonarCloud, point `SONAR_HOST_URL` to `https://sonarcloud.io`.

## AI Rules
The project includes AI-oriented repository rules:
- [Global rules](./.cursorrules)
- [Architecture rules](./.cursor/rules/architecture.md)
- [Testing rules](./.cursor/rules/testing.md)

## Documentation
- [Requirements](./docs/spec/requirements.md)
- [Architecture](./docs/spec/architecture.md)
- [Database](./docs/spec/database.md)
- [API](./docs/spec/api.md)
- [Frontend Guide](./docs/spec/frontend.md)
- [Deployment](./docs/spec/deployment.md)
- [Testing](./docs/spec/testing.md)
- [Quality](./docs/spec/quality.md)

## Security Notes
- JWT authentication
- Role-based access control
- Pydantic request validation
- Repository isolation for persistence logic
- Environment-based configuration

## Architecture Notes
The codebase explicitly uses:
- Repository pattern for persistence isolation
- Strategy pattern for listing sort behavior
- Factory pattern for database client creation

## Quality Goals
- Coverage target: `70%+`
- Expanded unit and integration suite for edge cases and role flows
- XML and HTML reports in CI artifacts
- Sonar Quality Gate support in pipeline
