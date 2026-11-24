# Feature Specification — F-022 Password Reset Email Delivery

- Status: Implemented
- Owner: Project team
- Related backlog item: F-022
- Related ADRs: none required (no new boundary, vendor lock-in, or data-model strategy change; SMTP is hidden behind an adapter)

## 1. Problem and objective
`POST /api/v1/auth/forgot-password` answered with a constant «Reset link sent»
and the UI then told users that email delivery was not active yet. Nothing was
sent, so a user who forgot their password could not recover the account. This
feature really emails a single-use reset link and resolves the ambiguity with a
matching reset page.

## 2. Actors and permissions
- Public visitors (signed out) can request a reset link and complete a reset.
- No authentication is required; possession of the emailed token is the proof.

## 3. Scope
### In scope
- `password_reset_tokens` table: hashed token, expiry, used-at, created-at.
- `POST /api/v1/auth/forgot-password`: creates a token when the address is
  registered and sends an email through the configured SMTP relay.
- `POST /api/v1/auth/reset-password`: consumes a token, stores a new Argon2id
  hash, revokes every refresh-token family, invalidates other pending tokens.
- SMTP adapter behind an `EmailSender` protocol; delivery failures are reported.
- `/reset-password` frontend page and the updated forgot-password success copy.

### Out of scope
- Email verification on registration (F-021) and notification emails (F-009).
- Provider-specific HTTP SDKs, templates managed in a vendor dashboard.
- Rate limiting infrastructure beyond the per-account resend cooldown.

## 4. Functional requirements
- FR-F022-001: A reset request never reveals whether an address is registered;
  both cases return `200 {"message": "Reset link sent"}`.
- FR-F022-002: For a registered address, a random 256-bit token is stored only
  as a SHA-256 hash and emailed as `{frontend}/reset-password?token=...`.
- FR-F022-003: Tokens expire after `PASSWORD_RESET_TTL_MINUTES` (default 30) and
  are single-use.
- FR-F022-004: Repeated requests within `PASSWORD_RESET_RESEND_SECONDS`
  (default 60) send no additional email but keep the same response.
- FR-F022-005: If the relay is not configured or rejects the message, the token
  is discarded and the client receives `EMAIL_NOT_CONFIGURED` (503) or
  `EMAIL_DELIVERY_FAILED` (502) — never a success claim.
- FR-F022-006: A successful reset revokes all refresh tokens of the account and
  marks every outstanding reset token used.
- FR-F022-007: The reset page validates the password (min 8) and confirmation,
  and shows Persian messages for expired/used links.

## 5. Business rules and invariants
- Raw tokens are never persisted or logged; only their SHA-256 hash is stored.
- The reset link points at the configured frontend origin, never at the API.
- Passwords are re-hashed with Argon2id; the policy matches registration.

## 6. Acceptance criteria
- Given a registered address and a working relay, one email containing a reset
  link is sent and the response is unchanged from the unknown-address case.
- Given a valid token, the password changes, the old password fails, and the
  token cannot be reused.
- Given an expired or unknown token, the API returns `INVALID_RESET_TOKEN` (400).
- Given a relay failure, the API returns 502 and leaves no usable token.

## 7. UX/API behavior
Error envelope as in AGENTS.md §6. The forgot-password page shows
«درخواست بازیابی ثبت شد، ایمیل خود را بررسی کنید» only after the API accepted
the request; delivery failures render the Persian error instead.

## 8. Data impact
New table `password_reset_tokens` (one row per issued link, cascade delete with
the user). No existing columns change; the migration is reversible.

## 9. Security and privacy
Tokens are 256-bit, hashed at rest, expiring, single-use, and invalidated as a
group when one is consumed. Enumeration is prevented by the constant response.
The trade-off is documented: during a relay outage the 5xx response can reveal
that an address exists; that is accepted over telling every user a lie.

## 10. Test strategy
Backend: integration tests with a fake `EmailSender` dependency covering the
happy path, unknown addresses, cooldown, relay failure, replay, expiry, session
revocation, and payload validation. Frontend: component tests for the reset page
and the updated forgot-password copy.
