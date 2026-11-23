# Implementation Plan — F-005 Routine CRUD

- Status: Approved
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
- [ ] Backend tests pass.
- [ ] Frontend tests pass.
- [ ] Soft-delete works (recoverable in DB, hidden in UI).
- [ ] Ownership is strictly enforced.
