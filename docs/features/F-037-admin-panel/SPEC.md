# F-037 — Admin panel: dashboard, users, mentorship, content, system

## Problem

F-030 shipped an admin *shell* with placeholder pages. Platform administrators
still had no way to see platform health, moderate accounts, supervise
mentorships, publish ready-made routines, or announce platform-wide messages.

## Actors

- Platform Administrator (`role = "admin"`). Every endpoint is gated by
  `require_role("admin")`.
- Regular user and mentor: never granted direct access; their records appear in
  the administrator's views.

## Scope

1. **Dashboard** — total users, routines, mentors, pending mentorship requests,
   active mentorships, programs, templates, categories, broadcasts, users active
   today, and a 14-day activity series (sign-ups, routines created, distinct
   users creating content).
2. **User management** — search by email/name/username, filter by role and
   status (active/disabled/banned), paginated list, ban/unban, enable/disable,
   and a one-time temporary password reset.
3. **Mentorship** — review the mentor-application queue (approve promotes the
   role, reject leaves it a user), list active mentors with client load, remove
   a mentor (demote and revoke grants), assign a mentor to a user, and read any
   mentor/client conversation for supervision.
4. **Content** — CRUD for routine templates (title, description, category,
   duration, publish flag) and habit categories (name, description, colour).
5. **System** — send broadcast announcements and read the system log filtered by
   level and free text.

## Non-goals

- No user-facing template adoption screen and no in-app broadcast inbox in this
  feature (the data is stored and listed; delivery surfaces are follow-ups).
- No plan/subscription management (F-013 remains separate).
- No deletion of accounts.

## Business rules

- Banned or disabled accounts receive `403 ACCOUNT_DISABLED` at login, on refresh,
  and on the next authenticated request; all refresh-token families are revoked
  when the flag is set.
- An administrator cannot ban or disable their own account, and another
  administrator's account cannot be banned or disabled.
- A temporary password is generated server-side, returned once, and never logged.
- Removing a mentor revokes their grants but keeps historical messages and
  programs that belong to users.
- Assigning a mentor on the user's behalf replaces any other active grant, so the
  one-mentor-at-a-time rule still holds.
- Every mutation appends an `audit` entry to `system_logs`. Failed API requests
  are recorded as `warning`/`error` by the request middleware.
- Requests are paginated (`limit`, `offset`); no unbounded list is exposed.

## API

`/api/v1/admin` — `GET /dashboard`, `GET /users`, `POST /users/{id}/ban`,
`POST /users/{id}/activation`, `POST /users/{id}/reset-password`,
`GET /mentors`, `POST /mentors/{id}/remove`, `POST /mentors/assign`,
`GET /conversations`, `GET /conversations/messages`, `GET|POST /templates`,
`PUT|DELETE /templates/{id}`, `GET|POST /categories`, `PUT|DELETE /categories/{id}`,
`GET|POST /broadcasts`, `DELETE /broadcasts/{id}`, `GET /logs`.

## Data impact

Migration `b3c1d7e9a2f4`: `users.is_active`, `users.is_banned`, and new tables
`habit_categories`, `routine_templates`, `broadcasts`, `system_logs`.

## Security and privacy

- Admin-only, deny by default; the browser's role is never trusted.
- Conversation supervision is an explicitly privileged read and is limited to
  what is already stored between a consenting pair.
- No passwords or tokens are written to the system log.

## Acceptance criteria

- A non-admin receives `403 FORBIDDEN` on every `/api/v1/admin` route.
- Banning a user blocks their next login with `ACCOUNT_DISABLED` and their
  existing access token stops working.
- The temporary password returned by a reset logs the user in.
- Templates and categories validate and audit their mutations.
- The dashboard reports accurate counters on an isolated database.
- The admin UI renders all five sections in Persian (RTL) with Element Plus.
