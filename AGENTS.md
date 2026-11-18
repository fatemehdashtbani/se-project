# AGENTS.md

> **Read this file before doing anything in this repository.**
> This document is the single source of truth for how software is designed, built,
> tested, and documented in this project. Any human or AI agent contributing to this
> repository MUST comply with the rules defined here.

---

## 1. Purpose

This repository hosts **Routine Manager** — a professional SaaS platform for
individuals and mentors to create, schedule, track, and analyze daily, weekly,
and monthly routines (habits, tasks, recurring activities). The project follows
**strict software engineering discipline**: spec-driven development, TDD,
architecture decision records, and living documentation.

Every contribution — human or AI-generated — is expected to be **reproducible,
auditable, testable, and documented**.

---

## 2. Product Scope (High Level)

Initial capabilities (each will become its own SPEC/PLAN feature):

1. **Authentication & RBAC** — sign-up/login with JWT; three roles: **User**,
   **Mentor**, **Admin**
2. **User profile & onboarding**
3. **Routine CRUD** — daily/weekly/monthly habits and tasks
4. **Routine scheduling** — recurring patterns (weekly, custom RRULE-like)
5. **Check-in tracking** — mark done/not done with optional note
6. **Dashboard & analytics** — streaks, completion rate, trends
7. **Reminders & notifications** — email + Android push
8. **Mentor discovery** — browse and select a mentor
9. **Mentor access** — mentor views assigned user's routines **only with the
   user's explicit, revocable consent**
10. **Mentor messaging** — comments on routines, direct messages
11. **Subscription plans** — Free / Paid; plan limits enforced server-side
12. **Admin panel** — web-only; user management, plan management, monitoring
13. **Android app** — notifications, check-ins, routine viewing (tech stack in
    ADR-0004)

**Non-goals (for now):** iOS app, public marketplace, native desktop, advanced
invoicing (separate ADR later).

---

## 3. Technology Stack

### Backend
- **Python 3.12+**
- **FastAPI** (async), **Uvicorn**
- **SQLAlchemy 2.0 (async)** + **Alembic** for migrations
- **PostgreSQL 16**
- **Redis 7** (cache + queue)
- **ARQ** (or Celery) for background jobs
- **Pydantic v2** for schemas & settings
- **pytest**, **pytest-asyncio**, **httpx.AsyncClient**, **testcontainers**,
  **freezegun**
- **ruff**, **mypy (strict)**, **pre-commit**

### Frontend (Web)
- **Vue 3** (Composition API, `<script setup>`)
- **TypeScript** (strict)
- **Vite**
- **Pinia** (state), **Vue Router 4**
- **TailwindCSS** + **shadcn-vue**-style primitives
- **zod** + **vee-validate** (forms)
- **Vitest** + **@vue/test-utils** (unit), **Playwright** (E2E)
- **ESLint** + **Prettier**

### Mobile (Android)
- **Tech stack: TBD** — see `docs/adr/0004-mobile-tech-stack.md`
- Candidates: Flutter / React Native / Kotlin (decision required before
  feature `android-app` starts)
- MUST consume the same `/api/v1` REST API as the web frontend

### Infra / Ops
- **Docker** + **docker-compose** (local dev)
- **GitHub Actions** (CI: lint, type-check, test, build)
- **Conventional Commits**

> **Every new dependency requires justification** in the current feature's
> `PLAN.md` under a "Dependencies & Rationale" section.

---

## 4. Repository Layout

```
routine-manager/
├── AGENTS.md
├── Task-List.md
├── README.md
├── docker-compose.yml
├── docs/
│   ├── adr/
│   │   ├── 0001-record-architecture-decisions.md
│   │   ├── 0002-use-fastapi-and-sqlalchemy-async.md
│   │   ├── 0003-choose-jwt-over-session.md
│   │   ├── 0004-mobile-tech-stack.md        # TBD
│   │   └── ...
│   ├── features/
│   │   ├── 001-user-auth/
│   │   │   ├── SPEC.md
│   │   │   └── PLAN.md
│   │   └── ...
│   └── diagrams/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config, security, logging, exceptions
│   │   ├── api/             # routers (v1)
│   │   ├── domain/          # entities, value objects, services, ports
│   │   ├── infrastructure/  # db, cache, queue, external clients, adapters
│   │   └── schemas/         # pydantic I/O models
│   ├── alembic/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── app/             # router, layout, providers
│   │   ├── features/        # feature-sliced modules
│   │   ├── shared/          # components, composables, utils, api client
│   │   └── assets/
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/
│   ├── package.json
│   └── vite.config.ts
├── mobile/                  # Android app (tech TBD — see ADR-0004)
│   └── README.md
└── .github/workflows/
```

**Backend architectural style:** layered / hexagonal — `api → domain ← infrastructure`.
Dependencies point inward only.

**Frontend architectural style:** feature-sliced design
(`features/<name>/{api,components,composables,stores,pages,types}`).

---

## 5. Documentation is Non-Negotiable

### 5.1 Every feature MUST have a `SPEC.md` and a `PLAN.md`

Located at `docs/features/<NNN-feature-slug>/`.

- **`SPEC.md` (What & Why):** user stories, acceptance criteria, edge cases,
  API contract, data model, UI/UX flows, non-functional requirements,
  out-of-scope.
- **`PLAN.md` (How & When):** technical approach, task breakdown with
  checkboxes, TDD test list (Red first), dependencies & rationale, risks,
  rollback plan.

> **No production code may be written for a feature before its `SPEC.md` and
> `PLAN.md` exist and are reviewed/approved.**

### 5.2 Every architectural decision MUST have an ADR

Located at `docs/adr/NNNN-kebab-title.md`, following the Michael Nygard format.
**Never modify a past ADR** — write a new one that supersedes it.

Decisions that require an ADR include (non-exhaustive):
- Language / framework / major library choice
- Database schema approach (normalization, soft-delete, multi-tenancy)
- Auth mechanism (JWT vs session, refresh token strategy, OAuth providers)
- RBAC model (roles, permissions, storage)
- Async/queue strategy
- API versioning & error envelope
- Time zone storage convention
- Mobile tech stack (ADR-0004)
- Subscription plan enforcement strategy
- Deployment topology

### 5.3 `Task-List.md` is the single source of truth for status

Every feature has an entry with links to its SPEC, PLAN, ADRs, and status.
Update it **on the same commit** that changes state.

---

## 6. Development Workflow (Strict Order)

For **each new feature**, follow these steps **in order**:

1. **Register** the feature in `Task-List.md` (status: `Backlog`).
2. **Write** `docs/features/NNN-slug/SPEC.md`.
3. **Review** the SPEC (self-review for solo work, PR review for teams).
4. **Write** `docs/features/NNN-slug/PLAN.md` (task breakdown + TDD test list).
5. **Create ADR(s)** for any architectural decision the feature introduces.
6. **Create a branch:** `feature/NNN-slug`.
7. **Implement with TDD** (see §7).
8. **Update** `Task-List.md` → `In Review`, then `Done` after merge.
9. **Update** affected docs (`README`, diagrams, API docs).

**Definition of "started":** SPEC + PLAN exist and the branch is created.
**Definition of "done":** see §15.

---

## 7. Test-Driven Development (Non-Negotiable)

**Cycle: Red → Green → Refactor.** No production code is merged without a test
that failed first and then passed.

### 7.1 Rules
- **Backend:** every domain service, use case, endpoint, and serializer is
  unit- or integration-tested. **Coverage target:** ≥ 85% line & branch on
  `app/domain` and `app/api`.
- **Frontend:** every composable, store, and non-trivial component is
  unit-tested with Vitest. **Coverage target:** ≥ 80% for `src/features/**`.
- **E2E:** Playwright tests cover every critical user journey end-to-end
  (sign-up → create routine → check in → view dashboard; mentor → view with
  consent → comment).
- **Bug fixes** start with a failing regression test.

### 7.2 Test Pyramid
| Level       | Tool                                | Scope                        |
|-------------|-------------------------------------|------------------------------|
| Unit        | pytest / Vitest                     | Functions, composables       |
| Integration | pytest + httpx + testcontainers     | API + DB + queue             |
| Contract    | Schemathesis (backend) / MSW (front)| API contract parity          |
| E2E         | Playwright                          | Browser flows                |

### 7.3 Test Naming
- Backend: `test_<unit>_<scenario>_<expected>()`
- Frontend: `describe("<Component>") / it("should …")`
- Feature tests reference SPEC acceptance criteria by ID,
  e.g. `# SPEC-AC-03` in a docstring/comment.

---

## 8. Coding Standards

### 8.1 Backend (Python / FastAPI)
- **Async everywhere**; never call blocking I/O in async paths.
- **No business logic in routers** — routers call `domain/services`.
- **Pydantic schemas** for all I/O; never expose ORM models directly.
- **Explicit return types**; `mypy --strict` must pass.
- **Dependency Injection** via FastAPI `Depends`; no globals.
- **Error handling:** raise domain exceptions; a single exception handler
  maps them to the standard error envelope (see §10).
- **Config:** via `pydantic-settings`; secrets never in code or git.
- **Logging:** `structlog` JSON in prod, human-readable in dev.
  Never log secrets/PII.
- **SQLAlchemy:** models in `infrastructure/db/models/`; all queries via
  repository pattern in `infrastructure/db/repositories/`.

### 8.2 Frontend (Vue 3 + TS)
- `<script setup lang="ts">` only. No Options API.
- Components are **presentational** or **feature-scoped**; no cross-feature
  imports.
- **State:** Pinia per-feature store; global stores only for auth & theme.
- **API calls** centralized in `src/shared/api/http.ts` with typed clients
  per feature in `features/<name>/api/`.
- **Types:** shared API types in `src/shared/types/api.ts` (mirror backend
  schemas — ideally generated via `openapi-typescript`).
- **Styling:** TailwindCSS utility-first; no inline styles; design tokens
  in `tailwind.config.ts`.
- **Accessibility:** WCAG 2.1 AA minimum (labels, focus states, keyboard
  nav, ARIA where required).

### 8.3 General
- Max function length: **50 lines**. Max file length: **400 lines**.
- No commented-out code. No `TODO` without a linked issue.
- No magic numbers/strings — use named constants.
- No `console.log` / `print` in production code paths.

---

## 9. Git & Branching

- **Branches:**
  - `main` — always deployable.
  - `feature/<NNN>-<slug>` — new features.
  - `fix/<short-slug>` — bug fixes.
  - `chore/<short-slug>` — non-functional.
  - `docs/<short-slug>` — docs only.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `perf:`.
  Scope is the feature ID when applicable: `feat(002): add routine CRUD`.
- **PRs:**
  - Title mirrors the commit style.
  - Body links the SPEC and PLAN.
  - CI must be green (lint, type-check, tests, build).
  - At least 1 reviewer (or self-review checklist for solo mode).
  - Squash-merge into `main`.

---

## 10. API Design Guidelines

- **REST, JSON, `/api/v1`** prefix.
- **Resource-oriented URLs:** `/users`, `/routines`, `/check-ins`,
  `/mentors`, `/admin/users`.
- **HTTP verbs:** GET (safe), POST (create), PUT/PATCH (update), DELETE.
- **Status codes:** 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500.
- **Pagination:** cursor-based (`?cursor=&limit=`) with `next_cursor` in
  response.
- **Filtering & sorting:** explicit query params, documented in SPEC.
- **Idempotency:** POST endpoints that create billable/booked resources accept
  `Idempotency-Key` header.
- **Error envelope (mandatory):**
  ```json
  {
    "error": {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Routine not found",
      "details": { "id": "..." },
      "request_id": "..."
    }
  }
  ```
- **OpenAPI:** generated at `/api/v1/openapi.json`; frontend types derived
  from it.
- **Breaking changes** require a new API version AND an ADR.

---

## 11. Database & Migrations

- **Every schema change** goes through Alembic; **no manual SQL**.
- **Naming:** snake_case tables and columns; plural table names.
- **Migrations are forward-only** in `main`; write a companion downgrade
  when safe.
- **No destructive migration** (drop table/column) without an ADR and a
  data migration plan.
- **Time zones:** store all timestamps in **UTC**, `TIMESTAMPTZ`; users
  store their preferred time zone as IANA string. **ADR covers this.**
- **Soft delete** for user-facing records via `deleted_at TIMESTAMPTZ NULL`.
- **Indexes:** every FK is indexed; every unique constraint documented in
  SPEC.
- **RBAC storage:** role stored on `users.role` enum; mentor↔user relationship
  in a dedicated table with `granted_at` and `revoked_at` timestamps.

---

## 12. Security Checklist

Before marking any feature **Done**, verify:

- [ ] Input validated server-side (Pydantic) and client-side (zod).
- [ ] AuthN & AuthZ enforced on every non-public endpoint.
- [ ] **RBAC enforced:** User / Mentor / Admin role checks on every protected
      route.
- [ ] **Ownership checks:** users can only access their own routines and
      check-ins.
- [ ] **Consent-based mentor access:** mentor can only view a user's data if
      an active consent record exists; revoking consent immediately blocks
      access.
- [ ] **Plan limits enforced server-side** (e.g., free tier routine count
      limit), never trusted from client.
- [ ] **Admin endpoints** protected by `admin` role only, audited in logs.
- [ ] No secrets in code, logs, or git history.
- [ ] Rate limiting on auth & public endpoints.
- [ ] CSRF protection if cookie-based auth is used.
- [ ] SQL injection prevented (ORM/parameterized queries only).
- [ ] XSS prevented (no `v-html` on user input; sanitize markdown).
- [ ] Dependency vulnerabilities checked (`pip-audit`, `npm audit`).
- [ ] PII redaction in logs.

---

## 13. Observability

- **Structured logs** with `request_id`, `user_id`, `role` (when known).
- **Health endpoints:** `/healthz` (liveness), `/readyz` (readiness).
- **Metrics:** `prometheus-fastapi-instrumentator` for latency & error rates.
- **Tracing:** OpenTelemetry hooks (opt-in via env).
- **Audit log:** role-changing and consent-granting/revoking actions must be
  logged to a dedicated audit stream.

---

## 14. Feature Development Lifecycle (Concrete Example)

Let's say we want to add **Feature 003 — Routine CRUD**.

1. Append to `Task-List.md` under "Backlog":
   `| 003 | Routine CRUD | docs/features/003-routine-crud/SPEC.md | docs/features/003-routine-crud/PLAN.md | TBD | Backlog |`
2. Create `docs/features/003-routine-crud/SPEC.md` (user stories,
   acceptance criteria, API contract, data model, edge cases).
3. Create `docs/features/003-routine-crud/PLAN.md` (task list, test list,
   ADRs needed, risks).
4. Create ADRs if needed, e.g. `0005-routine-data-model.md`.
5. `git switch -c feature/003-routine-crud`.
6. **TDD:** write a failing test → run → see Red → implement minimal code →
   Green → refactor → repeat.
7. Open PR, get CI green, merge.
8. Update `Task-List.md` status → `Done`.

---

## 15. Definition of Done

A feature is **Done** only when **all** of these are true:

- [ ] `SPEC.md` and `PLAN.md` exist and match the shipped behavior.
- [ ] All ADRs for the feature are written and referenced in the PLAN.
- [ ] Unit + integration + E2E tests exist and pass.
- [ ] Coverage thresholds met (§7.1).
- [ ] `mypy --strict`, `ruff`, `eslint`, `tsc --noEmit` pass.
- [ ] No new `TODO`s without linked issues.
- [ ] Security checklist (§12) verified — **including RBAC & consent checks**.
- [ ] API contract updated in OpenAPI; frontend types regenerated.
- [ ] `Task-List.md` updated → `Done`.
- [ ] Demo/demo link recorded in PR (for UI features).

---

## 16. Templates

### 16.1 ADR Template (`docs/adr/NNNN-title.md`)

```markdown
# NNNN. <Short Title>

- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXXX
- **Date:** YYYY-MM-DD
- **Deciders:** @…
- **Related:** SPEC-…, PLAN-…

## Context
What is the problem / force at play?

## Decision
What did we decide to do?

## Consequences
### Positive
### Negative
### Neutral

## Alternatives Considered
- Option A — pros/cons
- Option B — pros/cons
```

### 16.2 SPEC Template (`docs/features/NNN-slug/SPEC.md`)

```markdown
# SPEC — <Feature Name>

- **Feature ID:** NNN
- **Status:** Draft | Review | Approved | Implemented
- **Owner:**
- **Related ADRs:**
- **Last updated:** YYYY-MM-DD

## 1. Summary
## 2. Motivation / Why
## 3. User Stories
- US-01: As a … I want … so that …
## 4. Acceptance Criteria
- AC-01 (given/when/then)
## 5. Functional Requirements
## 6. Non-Functional Requirements (perf, security, a11y, i18n, tz)
## 7. API Contract (endpoints, schemas, errors, examples)
## 8. Data Model (tables, fields, indexes, constraints)
## 9. UI / UX Flows (wireframes, states, empty/error/loading)
## 10. Edge Cases
## 11. Out of Scope
## 12. Open Questions
```

### 16.3 PLAN Template (`docs/features/NNN-slug/PLAN.md`)

```markdown
# PLAN — <Feature Name>

- **Feature ID:** NNN
- **SPEC:** ./SPEC.md
- **Status:** Draft | Approved | In Progress | Done

## 1. Technical Approach
## 2. Architecture & Decisions
- Introduces ADR-XXXX: …
## 3. Dependencies & Rationale
- `<package>` — used for …; alternatives considered …
## 4. TDD Test List (Red-first)
### Backend
- [ ] test_<…>
### Frontend
- [ ] should <…>
### E2E
- [ ] flow: sign-up → …
## 5. Task Breakdown
- [ ] Backend: domain model
- [ ] Backend: repository
- [ ] Backend: service
- [ ] Backend: API endpoint
- [ ] Backend: migration
- [ ] Frontend: API client
- [ ] Frontend: store/composables
- [ ] Frontend: UI components
- [ ] Frontend: page wiring
- [ ] E2E
- [ ] Docs update
## 6. Risks & Mitigations
## 7. Rollback Plan
## 8. Definition of Done (link to §15)
```

---

## 17. Ground Rules for AI Agents (and Humans)

1. **Never write production code without a SPEC + PLAN.**
2. **Never write production code without a failing test first.**
3. **Never make an architectural decision without an ADR.**
4. **Never skip updating `Task-List.md`.**
5. **Ask, don't guess.** If a requirement is ambiguous, request clarification
   before proceeding.
6. **Prefer the smallest viable change.** Small PRs, clear diffs.
7. **Documentation outlives code** — when in doubt, write it down.
8. **No `git push --force` to shared branches.**
9. **No secrets, ever.** Use `.env.example` for documentation.
10. **Leave the codebase better than you found it** — but scope refactors in
    their own `chore/` PR.

---

_Last updated: v1.1 — added Routine Manager scope, RBAC, mobile, subscriptions._
