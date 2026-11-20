# Implementation Plan — F-003 Role-Based Access Control

- Status: Approved
- Related SPEC: `SPEC.md`

## 1. Implementation approach
1. Create a dependency `require_role` that wraps `get_current_user`.
2. Write a seed script to create admin users directly in the DB.
3. Create a dummy protected route to test the dependency.
4. Update frontend types (User interface) to ensure `role` is strictly typed as `'user' | 'mentor' | 'admin'`.

## 2. Ordered tasks
1. **RED:** Write integration tests for `/api/v1/admin/test` expecting 401 (no auth), 403 (user token), and 200 (admin token).
2. **GREEN:** Implement `require_role` in `backend/app/api/dependencies.py`.
3. **GREEN:** Implement `/api/v1/admin/test` route.
4. **GREEN:** Write `backend/scripts/create_admin.py`.
5. **REFACTOR:** Update `frontend/src/stores/auth.ts` `User` interface to use a union type for `role`.

## 3. Completion checklist
- [x] Tests cover 401, 403, and 200.
- [x] Seed script works manually.
- [x] Linters and type-checkers pass.
