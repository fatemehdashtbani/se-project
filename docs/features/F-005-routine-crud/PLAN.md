# Implementation Plan — F-005 Routine CRUD

- Status: In Progress (backend complete; frontend pending)
- Related SPEC: `SPEC.md`

## 1. Implementation approach
1. Backend: Define `Routine` model, generate migration, write RED tests for endpoints, then implement services and routes.
2. Frontend: Create `useRoutineStore`, write RED tests, then build the UI.

## 2. Ordered tasks
1. **Backend RED:** Write tests for create, list, update, delete, and ownership.
2. **Backend GREEN:** Model, service, routes.
3. **Frontend RED:** Store tests and Dashboard UI tests.
4. **Frontend GREEN:** Implement store and UI.

## 3. Completion checklist
- [x] Backend tests pass (`tests/api/test_routines.py`, 14 tests).
- [ ] Frontend tests pass.
- [x] Soft-delete keeps the row in the DB (`deleted_at`, `is_active=False`) and hides it from the API.
- [ ] Soft-deleted routines are hidden in the UI (blocked on the frontend work).
- [x] Ownership is strictly enforced (foreign ids answer 404 `ROUTINE_NOT_FOUND`).
