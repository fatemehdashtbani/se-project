# Implementation Plan — F-019 Identity Backend — Registration, JWT sessions (Hybrid), Argon2

- Status: Approved
- Related SPEC: `SPEC.md`
- Related ADRs: ADR-0002, ADR-0005, ADR-0006

## 1. Implementation approach
1. Setup async SQLAlchemy and Alembic for SQLite (dev) and Postgres (prod).
2. Define the `User` model.
3. Implement security utils (Argon2 hashing, JWT creation/validation).
4. Build the API endpoints using TDD.

## 2. Ordered tasks
1. **Database Setup:** Add SQLAlchemy base, session manager, and Alembic init.
2. **RED:** Write failing tests for `/auth/register` (e.g., success, duplicate email, weak password).
3. **GREEN:** Implement User model, Argon2 hashing, and `/auth/register`.
4. **RED:** Write failing tests for `/auth/login` (e.g., success, wrong password).
5. **GREEN:** Implement JWT creation and `/auth/login` setting HttpOnly cookies.
6. **RED:** Write failing tests for `/auth/refresh` and `/auth/logout`.
7. **GREEN:** Implement refresh rotation and logout.
8. **REFACTOR:** Ensure mypy strict and ruff pass.

## 3. Test plan
- Use `pytest-asyncio` and `httpx.AsyncClient`.
- Database: Use an in-memory SQLite database for fast, isolated tests.
- Test security: Ensure passwords are hashed in the DB and cookies are HttpOnly.

## 4. Completion checklist
- [ ] DB migrations work.
- [ ] Tests pass on SQLite.
- [ ] Linters and type-checkers pass.
- [ ] API docs (OpenAPI) generated correctly.
