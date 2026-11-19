# Feature Specification — F-019 Identity Backend — Registration, JWT sessions (Hybrid), Argon2

- Status: Implemented
- Owner: Project team
- Related backlog item: F-019
- Related ADRs: ADR-0002 (DB), ADR-0005 (JWT Hybrid), ADR-0006 (RBAC)

## 1. Problem and objective
The frontend login UI (F-002) is currently mocked. We need real authentication endpoints, a database to store users, password hashing, and JWT session management to secure the application.

## 2. Actors and permissions
- Public visitors can access `/api/v1/auth/register` and `/api/v1/auth/login`.
- Authenticated users can access `/api/v1/auth/me` and `/api/v1/auth/logout`.

## 3. Scope
### In scope
- PostgreSQL (prod) / SQLite (dev) setup via SQLAlchemy and Alembic.
- `User` table: id, email, password_hash, role (default 'user'), timezone, created_at.
- Registration endpoint: validates email format, hashes password with Argon2id.
- Login endpoint: verifies credentials, issues JWT access token (15 min) and refresh token (14 days). Web clients receive them as HttpOnly cookies.
- Refresh endpoint: validates refresh token, rotates it, issues new access token.
- Logout endpoint: clears cookies and revokes refresh token.
- `GET /me` endpoint: returns current user profile.
- The `User` table will have a `timezone` column with a default of `UTC`. Users can change this later via `PUT /me/timezone`.
- A `refresh_tokens` table will track active refresh tokens (id, user_id, token_hash, expires_at, revoked_at) to enable server-side invalidation on logout.

### Out of scope
- Email verification sending (deferred to F-021).
- Password reset flow (deferred to F-022).
- Frontend integration (will be done in F-023).
- Android Bearer token flow (deferred to Phase 6).

## 4. Functional requirements
- FR-F019-001: Register with unique email and password (min 8 chars). Password stored with Argon2id.
- FR-F019-002: Login returns HttpOnly cookies (`access_token`, `refresh_token`).
- FR-F019-003: The access token expires in 15 mins; refresh token in 14 days.
- FR-F019-004: Refresh endpoint rotates the refresh token (prevents replay attacks).
- FR-F019-005: Logout invalidates the refresh token in the DB and clears cookies.
- FR-F019-006: The system must provide `GET /api/v1/auth/me` which returns the current user's profile (id, email, role, timezone). It authenticates strictly via the access token cookie.
- FR-F019-007: The system must provide `PUT /api/v1/auth/me/timezone` to update the user's IANA timezone. It must validate the timezone against the standard IANA database.
- FR-F019-008: Family-scoped logout: Logout revokes the entire token family.

## 5. Business rules and invariants
- Passwords must never be logged or returned in responses.
- Email must be lowercase and unique.

## 6. Acceptance criteria
- Given valid registration data, a user is created in the DB.
- Given invalid credentials, login returns 401.
- Given a valid refresh cookie, a new access cookie is issued.

## 7. UX/API behavior
Errors return a consistent JSON envelope: `{"error": {"code": "STABLE_CODE", "message": "Human readable"}}` as mandated by AGENTS.md §6.

## 8. Data impact
Adds two tables: `users` (one row per account) and `refresh_tokens` (one row per issued refresh token, retained for revocation and audit). Each refresh-token row carries a `family_id` identifying the login chain it belongs to, so rotation and replay detection are scoped per session and logout revokes only its own family. No existing data is migrated in this feature.

## 9. Security and privacy
All auth mutations (`register`, `login`, `refresh`, `logout`) will use `HttpOnly`, `Secure` (in prod), and `SameSite=Lax` cookies. CSRF protection is enforced by checking the `Origin`/`Referer` headers against the allowed frontend domain, or via double-submit cookie pattern.

## 10. Test strategy
- Integration tests using `pytest`, `httpx.AsyncClient`, and a test SQLite database.
- Test all endpoints, invalid inputs, and token expiry logic.
