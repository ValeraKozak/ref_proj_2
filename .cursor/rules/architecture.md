# Architecture Rules

## Current Style
The project uses a layered architecture:
- `src/controllers` for HTTP adapters
- `src/services` for business logic
- `src/repositories` for persistence logic
- `src/models` for domain entities
- `src/dto` for API contracts

## Boundaries
- Controllers should orchestrate request/response mapping only.
- Services should own validation beyond DTO shape checks, role rules, moderation rules, and domain workflows.
- Repositories should encapsulate MongoDB access and query details.
- Shared infrastructure concerns belong in `src/core` or `src/db`.

## Change Rules
- Prefer adding behavior to services before controllers.
- Keep repository methods cohesive and query-focused.
- Preserve numeric external ids even if MongoDB internals change.
- New features should add tests at the service layer and API layer when behavior is user-facing.

## Safety Rules
- Do not depend on a live external database in tests.
- Avoid direct raw persistence calls from controllers.
- Keep authentication, authorization, and upload handling isolated from listing/category business rules.
