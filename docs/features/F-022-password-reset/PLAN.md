# Implementation Plan — F-022 Password Reset Email Delivery

## Ordered steps
1. Settings: frontend base URL, token TTL, resend cooldown, SMTP relay fields.
2. `PasswordResetToken` model + Alembic migration `a4b1c2d3e4f5`.
3. Email port: `EmailSender` protocol, `EmailContent`, SMTP implementation,
   Persian reset-email renderer, `EMAIL_NOT_CONFIGURED` / `EMAIL_DELIVERY_FAILED`.
4. Service `app/services/password_reset.py`: create/consume/discard tokens,
   cooldown, session revocation.
5. Routes: real `forgot-password`, new `reset-password`, email-sender dependency.
6. Frontend: `resetPassword` store action, `/reset-password` page, updated
   forgot-password copy, Persian error codes.
7. Documentation: `Task-List.md` row and change log.

## Tests written first
- `tests/api/test_forgot_password.py`: link is emailed, identical response for
  unknown addresses, cooldown, relay failure leaves no token, validation.
- `tests/api/test_reset_password.py`: password change, single use, unknown and
  expired tokens, session revocation, payload validation, sibling invalidation.
- `frontend/src/views/__tests__/{ForgotPasswordPage,ResetPasswordPage}.spec.ts`.

## Migration and rollback
`alembic upgrade head` creates the table and its two indexes; `downgrade` drops
them. Removing the feature also requires clearing the SMTP settings.

## Documentation
This folder's `SPEC.md`, the `Task-List.md` row and change log, and
`backend/.env.example` for the SMTP variables.

## Completion checks
- `ruff`, `mypy`, `pytest` for the backend.
- `type-check`, `lint`, `test:unit`, `build` for the frontend.
- A live request against a real relay is required before claiming delivery; a
  configured SMTP relay is an operator responsibility.
