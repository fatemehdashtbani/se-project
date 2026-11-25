# F-033 — Implementation plan

## 1. Backend

1. Add `ChecklistItem`, `Note`, and `CalendarEvent` models to
   `app/infrastructure/db/models.py`, with `user_id` foreign keys and cascade
   relationships on `User`.
2. Add request/response schemas:
   - `app/schemas/checklist.py` (`ChecklistItemCreate/Update/Response`,
     `ChecklistListResponse` with `total` and `done`)
   - `app/schemas/note.py`
   - `app/schemas/calendar.py`
3. Add owner-scoped services (`app/services/checklist.py`, `notes.py`,
   `calendar.py`) mirroring the routine service: every lookup filters on
   `user_id`, and a missing row raises a resource-specific `AppError` with 404.
4. Add routers (`app/api/routes/checklist.py`, `notes.py`, `calendar.py`) and
   register them in `app/main.py`.
5. Generate migration `b7e2c9d4a1f0` (revises `a4b1c2d3e4f5`) creating the three
   tables, their owner indexes, `is_done` default, and downgrade steps.
6. Add `backend/tests/api/test_personal_tools.py`.

## 2. Frontend

1. Stores: `checklist.ts`, `notes.ts`, `calendar.ts` using `apiRequest`, with
   local list updates that mirror the server's representation.
2. Date helpers in `shared/utils/calendar.ts`: Jalali↔Gregorian conversion and
   month lengths (pure arithmetic, no ICU), Persian month/weekday labels,
   Persian digits, Saturday-first Jalali month cells, ISO Gregorian day keys.
3. Pages: `ChecklistPage.vue`, `NotesPage.vue`, `CalendarPage.vue` in the
   existing dark RTL shell with `BottomNav`; the calendar displays and selects
   Jalali days while the API keeps storing ISO Gregorian dates.
4. Router: `/checklist`, `/calendar`, `/notes` behind `requiresAuth`.
5. Dashboard: «ابزارهای من» card grid linking to the three pages, plus
   `BottomNav` links to the three tools on every signed-in page.
6. Tests: store wiring in `stores/__tests__/personal.spec.ts`, Jalali helpers in
   `shared/utils/__tests__/calendar.spec.ts`, and navigation links in
   `components/__tests__/BottomNav.spec.ts`.

## 3. Verification

```bash
# backend (from backend/)
./.venv/Scripts/python.exe -m ruff check app tests
./.venv/Scripts/python.exe -m mypy app
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m alembic upgrade head

# frontend (from frontend/)
npm run type-check
npm run lint
npm run test:unit -- --run
npm run build
```

## 4. Notes and follow-ups

- Calendar events are intentionally minimal (title + date). Recurring events,
  edit/move, and links to routines belong to F-006/F-007.
- The Jalali conversion is inlined from the arithmetic algorithm used by
  jalaali-js (MIT) instead of adding a new runtime dependency.
- The checklist is a single flat list per user; multiple lists would need a
  container table and a migration.
- No reminders are sent for calendar events; notifications remain F-009.
