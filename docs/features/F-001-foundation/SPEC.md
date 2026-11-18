# Feature Specification — F-001 Repository Foundation

- Status: Approved
- Owner: Project team
- Related backlog item: F-001
- Related ADRs: ADR-0001, ADR-0002, ADR-0010

## 1. Problem and objective
Bootstrap a reproducible development environment: frontend (Vue 3 + TS +
Vite + Tailwind + RTL) and backend (FastAPI + SQLAlchemy + Alembic) with
linting, type checking, and test runners. This is the prerequisite for all
subsequent features.

## 2. Actors and permissions
Developers only. No user-facing behavior in this feature.

## 3. User journeys
None (infrastructure feature).

## 4. Scope
### In scope
- `frontend/` Vue 3 + Vite + TypeScript + Tailwind + Vue Router + Pinia.
- RTL setup (`dir="rtl"`, `lang="fa"`) and Vazirmatn font.
- `backend/` FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2.
- `ruff`, `black`, `mypy`, `pytest`, `vitest`, `eslint`, `prettier`.
- `.env.example` files (no real secrets).
- `.gitignore` extensions for both sides.
- One placeholder route `/login` rendering a "Coming soon" page so the dev
  server can be verified end-to-end.

### Out of scope
- Real login form (that is F-002).
- Authentication logic.
- Database schema (Alembic baseline comes with F-002).
- CI (comes with F-017 or when a remote repo is created).

## 5. Functional requirements
- FR-F001-001: `npm run dev` in `frontend/` serves a Vite app on localhost.
- FR-F001-002: The app shows RTL layout with Vazirmatn font loaded.
- FR-F001-003: `npm run build` in `frontend/` succeeds.
- FR-F001-004: `uvicorn app.main:app --reload` in `backend/` serves `/healthz`.
- FR-F001-005: `ruff check`, `black --check`, `mypy` pass on backend.
- FR-F001-006: `eslint`, `vue-tsc --noEmit` pass on frontend.
- FR-F001-007: `pytest` and `vitest run` both pass (even with zero tests).

## 6. Business rules and invariants
None.

## 7. UX/API behavior
Only `/healthz` on backend. A "Coming soon" page at `/login` on frontend.

## 8. Data impact
None.

## 9. Security and privacy
No secrets in the repository. `.env.example` documents required variables.

## 10. Edge cases
None beyond toolchain compatibility on Windows.

## 11. Acceptance criteria
- Given a clean clone, When `cd frontend && npm install && npm run dev`,
  Then the app serves and shows an RTL page at `/login`.
- Given a clean clone, When `cd backend && pip install -e . && uvicorn
  app.main:app --reload`, Then `GET /healthz` returns 200.
- Given a clean clone, When both lint/type/test commands run, Then they
  exit 0.

## 12. Test strategy
- Backend: one `test_healthz.py` test verifying `/healthz` returns 200.
- Frontend: one `LoginPage.spec.ts` (placeholder) asserting the "Coming soon"
  text renders.

## 13. Dependencies and open questions
- None.

## 14. Definition of Ready
Approved; ADR-0010 (no Docker) and ADR-0002 (SQLite dev) apply.
