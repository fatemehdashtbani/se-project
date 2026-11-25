# F-035 — Mentor collaboration on the user dashboard

## Purpose

A signed-in user should be able to pick a mentor/consultant from the platform,
chat with them, and receive a plan (study, workout, life routine, …) that can be
turned into one of the user's own routines.

This is a deliberately small first slice of the mentor layer (F-010/F-011/F-012):
discovery, a one-mentor consent grant, a single 1:1 thread, and mentor-authored
programs with an "adopt as routine" action.

## Actors

- **User** — browses mentors on the dashboard, selects one (granting consent),
  chats, and adopts programs into their routines.
- **Mentor** — a user whose `role` is `mentor`. Sees only clients with an active
  grant, replies in the thread, and sends programs.

## Scope

In scope:

- Mentor directory built from accounts with `role = "mentor"` plus a mentor
  profile (headline + bio).
- One active mentor per user. Selecting a mentor records a consent grant;
  selecting another (or clearing) revokes the previous grant.
- One message thread per (user, mentor) pair; both sides can read and write it
  while the grant is active.
- Mentor-authored programs (`title`, `description`, `category`) delivered to a
  client; the client can adopt a program, creating a routine.
- Dashboard section for users; a minimal `/mentor` workspace for mentors.
- `backend/scripts/create_mentor.py` so operators can create mentor accounts and
  their public profile.

Out of scope: multiple simultaneous mentors, real-time websockets, attachments,
read receipts, mentor browsing filters/pagination, ratings, payments for mentor
access, admin verification workflow, and editing/deleting programs after they
are sent. F-010/F-011/F-012 remain the fuller specifications.

## User journeys

1. A user opens the dashboard, sees «مربی و مشاور», picks a mentor from the
   directory, and sees the mentor's card with a chat box and programs list.
2. The user writes a message; the mentor (signed in on `/mentor`) sees the client
   in their list, opens the thread, reads it, and replies.
3. The mentor sends a program (e.g. «برنامه درسی دو هفتهای», category `study`).
   It appears in the user's dashboard; «افزودن به روتین‌های من» creates a routine
   with the program's title and description, and the routine list updates.
4. The user clears the selected mentor; the consent is revoked and the mentor's
   next request is denied.

## Functional requirements

- **FR-F035-001** — `GET /api/v1/mentors` returns every account with
  `role = "mentor"` (whether or not a profile row exists), with a display name
  and optional headline/bio. Any authenticated user may call it.
- **FR-F035-002** — A user has at most one active grant. `PUT
  /api/v1/mentors/selected` upserts a grant and revokes any other active grant
  for that user. `DELETE /api/v1/mentors/selected` revokes the active grant and
  answers `204`. Grants are never hard-deleted.
- **FR-F035-003** — Messages are readable and writable only by the two
  participants of the pair and only while an active grant exists. A missing or
  revoked grant answers `403 MENTOR_ACCESS_DENIED`; this check runs on every
  request. Message bodies are trimmed, blank bodies are rejected, and the
  maximum length is 4,000 characters.
- **FR-F035-004** — A mentor sees clients through `GET
  /api/v1/mentors/me/clients`, which lists only users with an active grant.
  Responses never include the client's email or phone number.
- **FR-F035-005** — `POST /api/v1/mentor-programs` is mentor-only and requires an
  active grant for the target client. Categories are `study`, `sport`, `life`,
  `other`. Titles are required; descriptions may be empty.
- **FR-F035-006** — `POST /api/v1/mentor-programs/{id}/adopt` is user-only, works
  once per program, creates a `Routine` owned by the user with the program's
  title/description, stores `routine_id`, and answers `200` with the program.
  Adopting twice answers `409 PROGRAM_ALREADY_ADOPTED`.
- **FR-F035-007** — A user cannot read another user's programs or thread, and a
  mentor cannot adopt programs or send a program to a client without a grant.
  Foreign/unknown ids answer `404` for the user's own resources and `403` for
  grant-gated mentor operations.
- **FR-F035-008** — The dashboard section is rendered for `role === "user"`;
  `role === "mentor"` sees a link to `/mentor`, which is role-gated in the
  router (`requiresRole: "mentor"`) and enforced again on every backend call.

## Data model

| Table | Columns |
|---|---|
| `mentor_profiles` | `id`, `user_id` FK→`users.id` (CASCADE, unique), `headline` (120), `bio` (text), `created_at` |
| `mentor_grants` | `id`, `user_id` FK→`users.id` (CASCADE), `mentor_id` FK→`users.id` (CASCADE), `granted_at`, `revoked_at`; unique `(user_id, mentor_id)` |
| `mentor_messages` | `id`, `user_id`, `mentor_id`, `sender_id` FK→`users.id`, `body` (text), `created_at`; index on `(user_id, mentor_id, created_at)` |
| `mentor_programs` | `id`, `user_id`, `mentor_id`, `title` (200), `description` (text), `category` (20), `routine_id` FK→`routines.id` (SET NULL, nullable), `created_at`; index on `(user_id, mentor_id)` |

`user_id` is always the client and `mentor_id` the mentor. No client-supplied
actor id is trusted; the sender is the authenticated account.

## API

| Method | Path | Behaviour |
|---|---|---|
| GET | `/api/v1/mentors` | `{ items, total }` mentor directory |
| GET | `/api/v1/mentors/selected` | `{ mentor: … \| null }` current selection |
| PUT | `/api/v1/mentors/selected` | Body `{ mentor_id }`; grant + return mentor |
| DELETE | `/api/v1/mentors/selected` | Revoke the active grant (`204`) |
| GET | `/api/v1/mentors/me/clients` | Mentor-only `{ items, total }` |
| GET | `/api/v1/mentor-messages?mentor_id=&client_id=` | Thread; user passes `mentor_id`, mentor passes `client_id` |
| POST | `/api/v1/mentor-messages` | Body `{ mentor_id? , client_id?, body }` |
| GET | `/api/v1/mentor-programs?client_id=` | User's programs (mentor may filter by client) |
| POST | `/api/v1/mentor-programs` | Mentor-only `{ client_id, title, description?, category }` |
| POST | `/api/v1/mentor-programs/{id}/adopt` | Create the routine, store `routine_id` |

## UI

- Dashboard: a «مربی و مشاور» panel. Without a selection it lists mentors with
  headline/bio and a «انتخاب مربی» button. With a selection it shows the mentor,
  the thread (sender labels, Persian time), a message box, and the program list
  with category labels and «افزودن به روتین‌های من»; a «تغییر مربی» control
  revokes the grant.
- `/mentor`: mentor-only workspace with the client list, the selected client's
  thread and reply box, and a program form (title, category, description).
- Empty, loading and error states are shown in Persian; no placeholder claims of
  delivery beyond what the API confirmed.

## Edge cases

- A mentor account without a profile row still appears, with an empty headline.
- Promoting an account to mentor takes effect on the next request because the
  role is read from the database.
- Selecting the already-selected mentor re-grants (idempotent upsert).
- Clearing when nothing is selected answers `204`.
- A revoked grant blocks thread reads, writes, and new programs immediately.
- Adopting a program whose routine was deleted keeps `routine_id` nullable and
  still refuses a second adoption.
- Two users may chat with the same mentor without seeing each other's thread.

## Security and privacy

- Authorization is server-side on every call: role for mentor endpoints, active
  grant for pair-scoped data, and ownership for programs/adoption.
- Mentor discovery exposes only display name, headline, and bio of mentor
  accounts — never emails or phone numbers.
- Messages and program bodies are personal data and are excluded from logs.
- The router's role guard is a UX convenience only.

## Acceptance criteria

- Backend tests cover auth, discovery, grant/revoke, both-sided messaging,
  consent denial after revoke, mentor-only endpoints, program creation/adoption,
  validation, and cross-account isolation.
- Store/component tests cover selection, sending, adopting, and the lenient
  empty states.
- `ruff`, `mypy`, `pytest`, `vue-tsc`, `eslint`, `vitest`, and `npm run build`
  pass; the new migration upgrades and downgrades cleanly on SQLite.
- The dev database can be seeded with a mentor account via
  `scripts/create_mentor.py`, and the dashboard section is reachable in the
  running preview.
