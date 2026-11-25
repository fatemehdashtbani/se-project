# F-033 — Personal tools: checklist, calendar, notes

## Purpose

The dashboard currently offers routines only. This feature adds three small,
self-contained personal tools so a signed-in user can keep their day in one
place:

- **چک‌لیست** — a flat list of tasks with a done flag and a done/total counter.
- **تقویم** — a month grid with dated events the user adds and removes.
- **یادداشت‌ها** — free-form notes with a title and body.

## Scope

In scope: authenticated CRUD persisted in the backend, three pages, dashboard
entry points, and the API they call.

Out of scope: sharing, reminders/notifications, recurring checklist items,
richer calendar views (week/agenda), and linking events to routines. Routine
scheduling (F-006) stays separate.

## User journeys

1. From the dashboard's «ابزارهای من» cards or the shared bottom navigation the
   user opens any of the three tools; the bottom navigation stays available on
   every signed-in page, so the pages need no separate back link.
2. A user adds a checklist item, ticks it off (the counter updates), renames it,
   or deletes it.
3. A user creates a note, edits its title/body inline, or deletes it.
4. A user moves between Jalali months, picks a day, adds an event for it (the
   day gets a dot), and deletes events from the month list.

## Functional requirements

- **FR-F033-001** — Checklist items, notes, and calendar events are owned by the
  signed-in user. Every query is scoped by `user_id` from the session.
- **FR-F033-002** — A foreign or unknown id answers `404` with
  `CHECKLIST_ITEM_NOT_FOUND`, `NOTE_NOT_FOUND`, or `CALENDAR_EVENT_NOT_FOUND`;
  existence is never confirmed with `403`.
- **FR-F033-003** — Titles are trimmed and blank titles are rejected with `422`
  `VALIDATION_ERROR`. Note bodies may be empty; checklist toggles use
  `PUT { "is_done": true|false }`.
- **FR-F033-004** — Checklist updates are partial: only the fields present in the
  body change. An empty body is rejected.
- **FR-F033-005** — Calendar events carry an ISO Gregorian date (`YYYY-MM-DD`).
  The list endpoint accepts optional `start`/`end` date filters inclusive on both
  ends; the page loads the caller's events and filters by the visible Jalali
  month after converting each stored date.
- **FR-F033-006** — Deleting a checklist item, note, or event is a hard delete.
  Unlike routines, nothing references these rows.
- **FR-F033-007** — All pages require an authenticated session; the router guard
  sends signed-out visitors to `/login`.
- **FR-F033-008** — The shared bottom navigation links to the checklist, calendar
  and notes pages on every signed-in page.

## Data model

| Table | Columns |
|---|---|
| `checklist_items` | `id`, `user_id` FK→`users.id` (CASCADE), `title` (200), `is_done` (default false), timestamps |
| `notes` | `id`, `user_id` FK→`users.id` (CASCADE), `title` (200), `content` (text), timestamps |
| `calendar_events` | `id`, `user_id` FK→`users.id` (CASCADE), `title` (200), `event_date` (date), `created_at` |

Indexes: one on each `user_id` column.

## API

| Method | Path | Behaviour |
|---|---|---|
| GET | `/api/v1/checklist-items` | `{ items, total, done }` |
| POST | `/api/v1/checklist-items` | Create `{ title }` |
| PUT | `/api/v1/checklist-items/{id}` | Partial `{ title?, is_done? }` |
| DELETE | `/api/v1/checklist-items/{id}` | `204` |
| GET | `/api/v1/notes` | `{ items, total }`, most recently edited first |
| POST | `/api/v1/notes` | Create `{ title, content? }` |
| PUT | `/api/v1/notes/{id}` | Partial `{ title?, content? }` |
| DELETE | `/api/v1/notes/{id}` | `204` |
| GET | `/api/v1/calendar-events?start=&end=` | `{ items, total }` |
| POST | `/api/v1/calendar-events` | Create `{ title, event_date }` |
| DELETE | `/api/v1/calendar-events/{id}` | `204` |

## UI

- `/checklist` — add form, progress line («۲ از ۵ انجام شده»), checkbox list with
  strikethrough for done items, delete per row, Persian empty state.
- `/notes` — add form (title + body), cards with inline edit/save/cancel and
  delete, Persian empty state.
- `/calendar` — Jalali month header with previous/next/«امروز», Saturday-first
  Jalali grid with Persian month names and digits, dot on days with events, add
  form (title + selected Persian date, date defaults to today and is set by
  clicking a day), month event list with Persian dates and delete.
- Dashboard gains an «ابزارهای من» card grid linking to the three pages.
- `BottomNav` links to `/checklist`, `/calendar` and `/notes`, so the tools are
  reachable from every signed-in page; the three pages carry no separate
  «بازگشت به داشبورد» control.

## Edge cases

- Whitespace-only titles are rejected client-side and server-side.
- A Jalali month starting mid-week is padded with empty cells; rows always hold
  7 cells.
- Jalali↔Gregorian conversion is pure arithmetic with no ICU dependency, so the
  same grid and labels render in every browser.
- Deleting an item that another account owns leaves it untouched.
- Two accounts never see each other's items, notes, or events.
- Long note bodies are capped at 10,000 characters.

## Security and privacy

- Ownership comes from the access-token cookie via `get_current_user`; no client
  supplied user id is accepted.
- Responses omit `user_id`, so payloads do not leak account identifiers.
- No new secrets or third-party services are introduced.

## Acceptance criteria

- Backend tests cover auth-required access, lifecycle for all three resources,
  validation, date-window filtering, and cross-account isolation.
- Store tests cover fetch/create/update/toggle/delete wiring; Jalali conversion,
  month lengths, grid padding and day keys are unit-tested, and the bottom
  navigation links are covered.
- `ruff`, `mypy`, `pytest`, `type-check`, `lint`, `vitest`, and `build` pass.
- Migration `b7e2c9d4a1f0` upgrades and downgrades cleanly.
