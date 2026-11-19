# Implementation Plan — F-001 Repository Foundation

- Status: Approved
- Related SPEC: `SPEC.md`
- Related ADRs: ADR-0001, ADR-0002, ADR-0010

## 1. Implementation approach
Create minimal but correct scaffolds for both sides. Do not implement any
business logic. The goal is a running environment, not features.

## 2. Ordered tasks
1. Create `frontend/` with Vite, Vue 3, TypeScript, Tailwind, Vue Router,
   Pinia.
2. Configure RTL (`index.html` `dir="rtl"`) and Vazirmatn font in Tailwind
   theme.
3. Add placeholder `/login` route with "Coming soon" page.
4. Create `backend/` with FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2.
5. Add `GET /healthz`.
6. Add `ruff`, `black`, `mypy`, `pytest` configs.
7. Add `.env.example` and extend `.gitignore`.
8. Write one backend test (`/healthz`) and one frontend test (placeholder
   page) to verify the toolchain.

## 3. Database and migration plan
No schema yet. Alembic is initialized but `versions/` is empty. The baseline
migration arrives with F-002.

## 4. API and frontend plan
- `GET /healthz` → `{"status":"ok"}`.
- Frontend route `/login` → placeholder component.

## 5. Test plan
- Backend: `tests/test_healthz.py` — assert 200 and JSON body.
- Frontend: `src/views/__tests__/LoginPage.spec.ts` — assert "Coming soon"
  text renders.

## 6. Observability and operations
Backend has a single `/healthz`. No metrics yet.

## 7. Risks and mitigations
- Windows line-ending noise on commit → accept (documented in AGENTS.md).
- Node version mismatch → pin Node >= 20 in `package.json` engines.

## 8. Rollout and rollback
N/A (initial scaffold).

## 9. Completion checklist
- [x] `npm run dev` serves the frontend.
- [x] `uvicorn` serves `/healthz`.
- [x] `npm run lint && npm run type-check && npm run test:unit` pass.
- [x] `ruff check && black --check && mypy && pytest` pass.
- [x] `.env.example` exists.
