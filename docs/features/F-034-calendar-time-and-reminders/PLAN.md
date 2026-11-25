# F-034 — Implementation plan

1. **Red:** extend the calendar API test to create an event with
   `event_time: "14:30"` and assert the returned value, plus an event without a
   time; extend the store test to assert `event_time` in the POST body.
2. **Green (backend):** add `event_time` to the `CalendarEvent` model, the
   create/response schemas, the service signature, and the route call.
3. Add migration `d5a2f8c1e6b4` (`op.add_column` on `calendar_events`), with a
   downgrade that drops it.
4. **Green (frontend):** `formatEventTime` in `shared/utils/calendar.ts`, the
   `event_time` field and optional argument in `useCalendarStore.createEvent`,
   a time input on `/calendar`, and the time in the month list.
5. Add `TodayReminders.vue` and mount it in `App.vue`: fetch the user's events
   once, show today's events above `BottomNav`, dismiss per day, and send the
   optional browser notifications (summary + per-time timers).
6. Update `Task-List.md` and this folder's documents.

## Tests first

- `backend/tests/api/test_personal_tools.py` — time accepted, echoed, nullable.
- `frontend/src/stores/__tests__/personal.spec.ts` — POST body carries the time
  when set and omits it when empty.
- `frontend/src/shared/utils/__tests__/calendar.spec.ts` — Persian time label.

## Migration and rollback

`alembic upgrade head` adds the nullable column (existing rows get `NULL`).
`alembic downgrade -1` drops it. No data backfill is needed.

## Documentation

SPEC.md, PLAN.md and the `Task-List.md` entry for F-034.

## Completion checks

`cd backend && .venv/Scripts/python -m pytest -q`, `ruff check .`,
`mypy app`; `cd frontend && npx vue-tsc --noEmit`, `npx vitest run`,
`npm run lint`, `npm run build`.

No ADR: the change adds one nullable column and a client-side reminder; it does
not alter system boundaries, security, or deployment.
