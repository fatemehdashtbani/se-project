# Feature Specification — F-023 Frontend Auth Integration

- Status: Approved
- Owner: Project team
- Related backlog item: F-023
- Related ADRs: ADR-0005 (JWT Hybrid), ADR-0008 (FarsiUI)

## 1. Problem and objective
The Login UI (F-002) is currently mocked. We need to connect it to the FastAPI backend (F-019) so users can actually authenticate, store their session, and redirect to the dashboard.

## 2. Scope
### In scope
- Pinia store for auth (`useAuthStore`).
- Axios/fetch API client setup (with credentials: 'include').
- Connect `LoginPage.vue` to `POST /api/v1/auth/login`.
- Handle 401 errors (show Persian error message).
- On success, redirect to `/dashboard` (placeholder page for now).
- Add a route guard so `/dashboard` requires authentication.
- Add a logout button to the dashboard that calls `/logout` and redirects to `/login`.

## 3. Functional requirements
- FR-F023-001: The Login form must submit credentials to the backend.
- FR-F023-002: On success, the user's state is saved in Pinia.
- FR-F023-003: API errors must be displayed in Persian on the UI.
- FR-F023-004: Unauthenticated access to `/dashboard` must redirect to `/login`.
- FR-F023-005: Logout must clear state and cookies, redirecting to `/login`.

## 4. Test strategy
- Vitest: Mock the API client, test the Pinia store state, test the LoginPage error handling.
- Cypress/Playwright: Deferred to E2E phase.
