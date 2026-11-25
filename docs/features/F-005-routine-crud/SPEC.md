# Feature Specification — F-005 Routine CRUD

- Status: Approved
- Owner: Project team
- Related backlog item: F-005
- Related ADRs: ADR-0002 (DB), ADR-0006 (RBAC)

## 1. Problem and objective
The platform is useless without routines. Users need to create, view, edit, and delete their own routines. This is the foundational feature that all scheduling (F-006) and check-ins (F-007) will build upon.

## 2. Scope
### In scope
- Backend `Routine` SQLAlchemy model and Alembic migration.
- Endpoints: `POST /api/v1/routines`, `GET /api/v1/routines`, `GET /api/v1/routines/{id}`, `PUT /api/v1/routines/{id}`, `DELETE /api/v1/routines/{id}`.
- Enforce ownership: Users can only access their own routines.
- Frontend: `DashboardPage.vue` displays a list of the user's routines with inline create, edit (title and description), and delete controls.
- Frontend: Pinia store `useRoutineStore`.

### Out of scope
- Recurrence rules (F-006).
- Check-ins (F-007).
- Sharing with mentors (F-011).

## 3. Functional requirements
- FR-F005-001: Users can create a routine (title required, description optional).
- FR-F005-002: Users can list all their active routines.
- FR-F005-003: Users can update a routine's title or description.
- FR-F005-004: Users can soft-delete a routine (it disappears from the list).
- FR-F005-005: Users cannot access another user's routines (returns 404 or 403).

## 4. Data Model
- `Routine`: `id` (UUID), `user_id` (FK), `title` (str), `description` (str, optional), `is_active` (bool), `created_at`, `updated_at`, `deleted_at` (nullable).

## 5. Test strategy
- Backend: Pytest integration tests for all endpoints and ownership.
- Frontend: Vitest tests for the store and the dashboard rendering.
