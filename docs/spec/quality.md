# Якість та CI/CD

## Цільові метрики
- Code Coverage: `70%+`
- Test suite size: `200+`
- Bugs / Vulnerabilities: контролюються через SonarQube або SonarCloud
- Code Smells: контролюються через Sonar Quality Gate

## Поточна реалізація
У репозиторії налаштовано:
- `pytest` для unit та integration тестів;
- `pytest-cov` для coverage-метрик;
- `coverage.xml` для Sonar import;
- `pytest-report.xml` для test-report інтеграції;
- `htmlcov/` для візуального аналізу непокритих рядків;
- `ruff` як швидкий lint/static gate.

## GitHub Actions
Workflow [ci.yml](../../.github/workflows/ci.yml) виконує:
- збірку Python-залежностей;
- запуск lint;
- запуск тестів із XML та HTML coverage reports;
- upload quality artifacts;
- Sonar scan і Quality Gate, якщо задані secrets.

### Артефакти CI
Після кожного коміту pipeline зберігає:
- `coverage.xml`
- `pytest-report.xml`
- `ruff-report.txt`
- `htmlcov/`

Ці артефакти можна завантажити з GitHub Actions run і використати для ручної перевірки якості.

## SonarQube / SonarCloud
У проєкті вже є:
- [sonar-project.properties](../../sonar-project.properties)
- імпорт coverage і test reports
- conditional Sonar steps у CI

Для активації потрібно налаштувати GitHub secrets:
- `SONAR_TOKEN`
- `SONAR_HOST_URL`

Для SonarCloud як `SONAR_HOST_URL` використовується:
- `https://sonarcloud.io`

## Branch Protection
У GitHub Settings бажано увімкнути:
- required status check для `CI`
- required status check для Sonar Quality Gate
- заборону merge, якщо workflow або gate не пройшли

Це налаштування зберігається на рівні репозиторію GitHub, а не в коді.

## Поточний практичний стандарт команди
- кожна зміна бізнес-логіки супроводжується тестами;
- coverage та reports не вважаються опціональними;
- репозиторій підтримує AI-rules для більш контрольованої автоматизованої розробки;
- demo-дані не змінюються без окремого запиту.
