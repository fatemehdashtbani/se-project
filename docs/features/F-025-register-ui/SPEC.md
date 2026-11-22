# Feature Specification — F-025 Frontend Registration UI

- Status: Approved
- Owner: Project team
- Related backlog item: F-025
- Related ADRs: ADR-0008 (FarsiUI)

## 1. Problem and objective
Users currently cannot create an account from the frontend (they have to use Swagger). This feature adds a Registration page that connects to the existing `POST /api/v1/auth/register` endpoint, followed by an automatic login.

## 2. Scope
### In scope
- A Vue view `RegisterPage.vue` accessible at `/register`.
- Fields: Email, Password, Confirm Password.
- Validation: Email format, password min 8 chars, passwords must match.
- Connect to the backend register endpoint.
- On success, automatically log the user in (call the `login` action) and redirect to `/dashboard`.
- A link to navigate between `/login` and `/register`.
- Persian error messages (e.g., if email already exists).

### Out of scope
- Email verification.
- Captcha.

## 3. Functional requirements
- FR-F025-001: The `/register` route must render the form with RTL Persian labels.
- FR-F025-002: The form must validate that password and confirm-password match before submitting.
- FR-F025-003: On submit, call the `register` action in the Pinia store.
- FR-F025-004: Display backend errors (like `EMAIL_ALREADY_EXISTS`) in Persian.
- FR-F025-005: The Login page must have a link to this page, and vice versa.

## 4. Test strategy
- Vitest: Mock the store. Test validation (mismatched passwords), successful submission, and error rendering.
