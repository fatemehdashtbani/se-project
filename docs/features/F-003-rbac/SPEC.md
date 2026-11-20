# Feature Specification — F-003 Role-Based Access Control

- Status: Approved
- Owner: Project team
- Related backlog item: F-003
- Related ADRs: ADR-0006 (RBAC Model), ADR-0005 (JWT)

## 1. Problem and objective
Currently, any authenticated user has the same access. We need to enforce the three roles defined in ADR-0006 (User, Mentor, Admin). This feature creates the backend authorization dependencies to protect routes based on role.

## 2. Scope
### In scope
- A FastAPI dependency `require_role(role: str)` that checks the current user's role.
- Protect `admin` endpoints (to be created later) with `require_role("admin")`.
- A CLI script or seed mechanism to promote a user to `admin` (since we cannot self-assign).
- Unit and integration tests for 403 Forbidden scenarios.

### Out of scope
- The frontend UI for roles (this is F-014 Admin Panel).
- Mentor-specific endpoints (deferred to F-010).
- Custom sub-roles for admins (deferred via future ADR).

## 3. Functional requirements
- FR-F003-001: The backend must expose a dependency that returns a 403 Forbidden if the user lacks the required role.
- FR-F003-002: A script (`scripts/create_admin.py`) must exist to manually seed an admin user in the database.
- FR-F003-003: Accessing a `user` endpoint with an `admin` token must succeed if the endpoint doesn't strictly forbid admins (though most will just use `get_current_user`).

## 4. Test strategy
- Add a test endpoint `GET /api/v1/admin/test` that requires the `admin` role.
- Test with a normal user -> expects 403.
- Test with an admin user -> expects 200.
- Test with an unauthenticated request -> expects 401.
