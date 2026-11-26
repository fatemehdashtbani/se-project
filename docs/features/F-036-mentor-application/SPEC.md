# F-036 — Mentor application and admin approval

## Purpose

A regular user who wants to work on the platform as a mentor must ask first.
The request collects expertise, biography and evidence, waits as `pending`, and
becomes a mentor account only after an administrator approves it. This replaces
the operator-only `create_mentor.py` path for self-service onboarding while
keeping role changes under administrative control.

## Actors

- **User** — sends the request from their dashboard, sees its review state, and
  can correct and resubmit after a rejection.
- **Admin** — reviews the queue and approves or rejects requests.

## Scope

In scope:

- One application row per account with `pending` / `approved` / `rejected`.
- Dashboard entry «درخواست همکاری به عنوان مربی» and a dedicated
  `/become-a-mentor` page with expertise, biography and documents fields.
- Admin queue at `/admin/mentor-applications` with approve/reject actions.
- Approval sets `users.role = "mentor"` and upserts the public
  `mentor_profiles` row (headline from the expertise, bio from the request) so
  the new mentor appears in the F-035 directory immediately.

Out of scope: file uploads (documents are typed links/notes), review comments
back to the applicant, notifications/email, a full audit log (F-014), and
withdrawing an approved role.

## User journey

1. A signed-in user opens the dashboard and clicks «درخواست همکاری به عنوان مربی».
2. On `/become-a-mentor` they fill «حوزه تخصص», «بیوگرافی» and optionally
   «مدارک و سوابق», then submit. The page reports that the request is pending.
3. The dashboard and the page both show «در انتظار تایید» while it is reviewed.
4. An administrator opens `/admin/mentor-applications`, reads the request and
   approves it. The applicant's role and public mentor profile update.
5. After signing in again with the «مربی» role selected, the applicant reaches
   `/mentor`. A rejected request shows the reason state and a prefilled form.

## Functional requirements

- **FR-F036-001** — `GET /api/v1/mentor-applications/me` returns
  `{ application: … | null }` for the authenticated account, whatever the state.
- **FR-F036-002** — `POST /api/v1/mentor-applications` is user-only, trims all
  text, requires expertise (≤200) and biography (≤5,000), accepts optional
  documents (≤2,000, stored as NULL when blank), and stores `pending`.
  Submitting again updates the same row and resets it to pending; a mentor
  account is refused (`403 FORBIDDEN`).
- **FR-F036-003** — An administrator lists requests with `GET
  /api/v1/admin/mentor-applications?status=` (`pending`/`approved`/`rejected`,
  omitted for all), oldest first, with the applicant's display name and email.
- **FR-F036-004** — `POST /api/v1/admin/mentor-applications/{id}/approve` sets
  `approved`, `reviewed_at` and `reviewed_by`, promotes the applicant's role to
  `mentor`, and upserts their `MentorProfile` (headline = first 120 characters of
  the expertise, bio = the request's biography).
- **FR-F036-005** — `POST /api/v1/admin/mentor-applications/{id}/reject` sets
  `rejected` and leaves the account's role unchanged. Reviewing a non-pending
  request answers `409 MENTOR_APPLICATION_NOT_PENDING`; an unknown id answers
  `404 MENTOR_APPLICATION_NOT_FOUND`.
- **FR-F036-006** — Application endpoints require authentication (`401`);
  submission requires the `user` role and review requires `admin` (`403`
  otherwise). The frontend route guards are conveniences only.
- **FR-F036-007** — The dashboard shows the entry and current state to
  `role === "user"` accounts only; `/become-a-mentor` is `requiresAuth` and
  `/admin/mentor-applications` is role-gated to `admin`.

## Data model

| Table | Columns |
|---|---|
| `mentor_applications` | `id`, `user_id` FK→`users.id` (CASCADE, unique), `expertise` (200), `bio` (text), `documents` (text, nullable), `status` (20, default `pending`), `created_at`, `updated_at`, `reviewed_at` (nullable), `reviewed_by` FK→`users.id` (SET NULL, nullable); index `(status, created_at)` |

## API

| Method | Path | Behaviour |
|---|---|---|
| GET | `/api/v1/mentor-applications/me` | Caller's application or `null` |
| POST | `/api/v1/mentor-applications` | Create/resubmit as pending (`201`) |
| GET | `/api/v1/admin/mentor-applications?status=` | Admin queue `{ items, total }` |
| POST | `/api/v1/admin/mentor-applications/{id}/approve` | Approve + promote |
| POST | `/api/v1/admin/mentor-applications/{id}/reject` | Reject |

## UI

- Dashboard section «همکاری به عنوان مربی» with a status line and a link button
  «درخواست همکاری به عنوان مربی» to `/become-a-mentor`.
- `/become-a-mentor`: status banner for pending/approved/rejected, the form with
  Persian labels and validation messages, and a success notice after submission.
  A mentor account sees «شما مربی هستید» and a link to `/mentor` instead.
- `/admin/mentor-applications`: queue cards with applicant name/email, expertise,
  biography, documents and date; «تایید» / «رد درخواست» for pending rows and a
  Persian empty state. The admin sidebar gains «درخواست‌های مربیگری».

## Edge cases

- A rejected application keeps its id and can be resubmitted; `reviewed_at` and
  `reviewed_by` are cleared when it returns to pending.
- A pending application cannot be edited; the queue already holds its details.
- Approving twice fails with `409`; the account already being a mentor also
  fails (`403` at the route gate).
- An approved application whose role was changed by hand is still refused on
  resubmission instead of being pushed back into review.
- A blank optional documents field is stored as `NULL`, not an empty string.

## Security and privacy

- Role changes happen only through the admin-gated endpoints; the client can
  never send its own role. Roles are read from the database on every request.
- Applicant email is exposed only in the admin queue, not in mentor responses.
- Texts are trimmed and length-bounded; no HTML is rendered.
- Applications and biographies are personal data and stay out of logs.
- No audit table exists yet; a durable audit trail for role changes remains part
  of F-014.

## Acceptance criteria

- Backend tests cover auth, submission/resubmission, admin-only review,
  approval promotion + public profile, rejection, status filtering, validation
  and unknown ids.
- Frontend tests cover the dashboard entry and state, the application form and
  its pending/rejected/mentor states, and the admin approve/reject queue.
- `pytest`, `ruff`, `mypy`, `vitest`, `vue-tsc`, `eslint` and the production
  build pass, and the migration upgrades and downgrades cleanly.
