# Implementation Plan — F-031 Profile and Password Persistence

- Related spec: `docs/features/F-031-profile-persistence/SPEC.md`
- Related backlog item: F-031

## 1. Ordered steps

1. **Backend tests first (red)**
   - `backend/tests/api/test_profile.py`: persistence, partial update,
     validation failures, unauthenticated access.
   - `backend/tests/api/test_password.py`: hash replacement, old password
     rejected, wrong current password, validation, session revocation, auth
     requirement.
2. **Schemas** (`backend/app/schemas/auth.py`)
   - Extract `normalize_person_name` / `normalize_phone_number` so registration
     and the profile update share one rule.
   - Add `ProfileUpdateRequest` (partial, at least one field, no explicit nulls)
     and `ChangePasswordRequest`.
3. **Application service** (`backend/app/services/identity.py`)
   - `update_profile(session, user, payload)`.
   - `change_password(..., current_refresh_token)` with
     `InvalidCurrentPasswordError` and `_revoke_other_sessions`.
4. **HTTP routes** (`backend/app/api/routes/auth.py`)
   - `PUT /api/v1/auth/me` → `MeResponse`.
   - `PUT /api/v1/auth/me/password` → `{ "message": ... }`.
5. **Frontend tests first (red)**
   - `stores/__tests__/auth.spec.ts`: request shape for both actions.
   - `views/__tests__/ProfilePage.spec.ts`: store calls, success, failure.
6. **Frontend implementation**
   - `stores/auth.ts`: `updateProfile`, `changePassword`.
   - `views/ProfilePage.vue`: async submit handlers, submit disabling, Persian
     errors.
   - `shared/utils/errors.ts`: `INVALID_CURRENT_PASSWORD` message.
7. **E2E journey** (`frontend/e2e/auth.spec.ts`): save the profile and verify the
   values survive a reload.
8. **Docs**: this plan, the spec, and a `Task-List.md` entry.

## 2. Tests to write first

| Layer | File | Assertion focus |
| --- | --- | --- |
| Integration (API) | `backend/tests/api/test_profile.py` | Persistence, partial update, validation, 401 |
| Integration (API + DB) | `backend/tests/api/test_password.py` | Hash replaced, login behavior, other families revoked |
| Unit (store) | `frontend/src/stores/__tests__/auth.spec.ts` | Request method, body, and mirrored user |
| Component | `frontend/src/views/__tests__/ProfilePage.spec.ts` | Store calls, Persian messages, form lifecycle |
| E2E | `frontend/e2e/auth.spec.ts` | Profile values persist across a reload |

## 3. Migration and rollback

None. The columns and tables already exist, and the change only writes to them.
Rolling back the application code leaves the stored profile and password values
in place, which is acceptable (they are valid account data).

## 4. Documentation

- New feature folder with `SPEC.md` and `PLAN.md`.
- `Task-List.md`: F-031 row and a change-log entry.

## 5. ADR check

No ADR: the feature reuses the identity module, the existing cookie session
model (ADR-0005), and the existing Argon2id hashing. It adds no dependency, no
new boundary, and no data-model strategy change.

## 6. Completion checks

- `cd backend && .venv/Scripts/python.exe -m pytest tests -q`
- `cd frontend && npm run type-check && npm run lint && npm run test:unit`
- Ruff/format via the project's existing tooling where available.
