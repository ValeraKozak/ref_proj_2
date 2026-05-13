# Testing Strategy

## Goals
- Maintain coverage above 70 percent.
- Keep XML and HTML reports available in CI.
- Prefer explicit edge-case coverage over shallow happy-path duplication.

## Tooling
- `pytest`
- `pytest-cov`
- `mongomock`
- `httpx` / `fastapi.testclient`

## Test Layers
- Unit tests should target services, DTO validation, security helpers, and database bootstrap helpers.
- Integration tests should target REST API flows, auth, moderation, filtering, uploads, and permissions.

## Report Requirements
- Generate `coverage.xml` for SonarQube/SonarCloud ingestion.
- Generate `pytest-report.xml` for CI parsing.
- Generate `htmlcov/` for human-readable artifact download.

## Change Rules
- Every bug fix should include at least one regression test.
- Prefer `pytest.mark.parametrize` for validation matrices and role/permission permutations.
- Keep tests deterministic and isolated from developer-local services.
