# Feature Specification — F-031 Profile and Password Persistence

- Status: Implemented
- Owner: Project team
- Related backlog item: F-031
- Related ADRs: ADR-0005 (JWT strategy) — no new decision required

## 1. Problem and objective

The `/profile` page shipped with two display-only flows:

- the profile form ("نام", "نام خانوادگی", "شماره تلفن") only raised a Persian
  success message and never called the API;
- the "تغییر رمز عبور" form validated locally, closed, and claimed success
  without changing anything.

Users therefore saw "saved" confirmations for data that was never stored. This
feature makes both flows write to the database through the existing identity
module.

## 2. Actors

- Authenticated **User** (all roles share the same profile page).

## 3. Scope

### In scope

- `PUT /api/v1/auth/me` — update the signed-in user's `first_name`, `last_name`,
  and `phone_number`; returns the updated profile (`MeResponse`).
- `PUT /api/v1/auth/me/password` — verify the current password, store an Argon2id
  hash of the new password, and end every *other* session of that user.
- Frontend wiring in `ProfilePage.vue` and `useAuthStore` for both endpoints,
  including Persian success and error messages.

### Non-goals

- Changing the email address (email verification is a separate feature).
- Password strength policy beyond the existing 8-character minimum.
- Password reset / forgot-password delivery (F-022) — the endpoint remains a
  no-op mock because no email adapter/provider is configured yet.
- Avatar uploads.

## 4. Requirements

- FR-F031-001: `PUT /api/v1/auth/me` requires an authenticated session; an
  anonymous caller gets `401 UNAUTHORIZED`.
- FR-F031-002: Only the fields present in the body are applied. An empty body, a
  blank name, an explicit `null`, or a malformed phone number is rejected with
  `422 VALIDATION_ERROR`.
- FR-F031-003: Phone numbers are normalized with the same rule as registration
  (spaces and dashes removed, `^\+?[0-9]{7,15}$`).
- FR-F031-004: The response is the stored profile; `GET /api/v1/auth/me` returns
  the same values afterwards.
- FR-F031-005: `PUT /api/v1/auth/me/password` requires an authenticated session.
- FR-F031-006: A wrong current password yields
  `400 INVALID_CURRENT_PASSWORD` and changes nothing.
- FR-F031-007: A new password shorter than 8 characters, or a missing field,
  yields `422 VALIDATION_ERROR`.
- FR-F031-008: On success the old password no longer authenticates and the new
  one does.
- FR-F031-009: Every other refresh-token family of the user is revoked; the
  caller's own family (identified by the request's refresh cookie) keeps working,
  so the tab performing the change stays signed in.
- FR-F031-010: The profile page sends trimmed values and mirrors the server's
  response into the auth store; failures are shown with the shared Persian error
  mapping (`getPersianError`).
- FR-F031-011: The password form only closes after the server accepts the change.

## 5. Data impact

No schema change: `users.first_name`, `users.last_name`, `users.phone_number`,
and `users.password_hash` already exist (F-019 / F-026). Password changes update
`refresh_tokens.revoked_at` for other families. No migration required.

## 6. Security and privacy

- Current-password verification uses the existing Argon2id `verify_password`.
- Password hashes are never returned in any response.
- Session revocation limits the value of a stolen session after a password change.
- No secrets or plaintext passwords are logged.

## 7. Edge cases

- Account created before the profile fields existed (`NULL` names): filling the
  form stores real values.
- A client sending only one field updates only that field.
- A valid access token whose refresh family is already revoked still changes the
  password; no family is preserved in that case, so all remaining tokens are
  revoked.

## 8. Acceptance criteria

- Backend: `tests/api/test_profile.py` and `tests/api/test_password.py` pass.
- Frontend: `ProfilePage.spec.ts` proves the store is called with the form values
  and that success/error messages follow the API outcome.
- `npm run type-check`, `npm run lint`, `npm run test:unit` pass.
