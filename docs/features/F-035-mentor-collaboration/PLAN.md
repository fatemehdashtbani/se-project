# F-035 — Implementation plan

## 1. Data and backend

1. Models in `app/infrastructure/db/models.py`:
   `MentorProfile`, `MentorGrant` (unique `(user_id, mentor_id)`),
   `MentorMessage`, `MentorProgram` (nullable `routine_id`), with relationships on
   `User` where useful. New migration `e7b3f9a2c4d6` (revises `d5a2f8c1e6b4`).
2. Schemas in `app/schemas/mentor.py`: mentor summary, selection, message
   create/response/list, program create/response/list, category `Literal`.
3. Services in `app/services/mentors.py`:
   - `list_mentors`, `get_selected_mentor`, `select_mentor` (revokes other active
     grants), `revoke_selected_mentor`.
   - `_require_active_grant`, `_resolve_pair`, `list_messages`, `send_message`.
   - `list_clients`, `list_programs`, `create_program`, `adopt_program`.
   All lookups are scoped by the authenticated account; revoked grants are
   filtered in SQL.
4. Routers `app/api/routes/mentors.py` and `app/api/routes/mentor_programs.py`,
   registered in `app/main.py`; mentor-only routes use `require_role("mentor")`.
5. `backend/scripts/create_mentor.py` creates (or promotes) a mentor account and
   upserts its profile, following the `create_admin.py` CLI conventions.
6. Tests in `backend/tests/api/test_mentors.py` (Red first): auth, discovery,
   grant/switch/revoke, both-sided messaging, consent denial, program lifecycle,
   adoption and validation.

## 2. Frontend

1. `stores/mentor.ts`: typed `Mentor`, `MentorMessage`, `MentorProgram` state and
   actions `fetchMentors`, `fetchSelectedMentor`, `selectMentor`,
   `clearMentor`, `fetchMessages`, `sendMessage`, `fetchPrograms`,
   `adoptProgram`, plus the mentor-side `fetchClients`, `sendProgram`.
2. `components/MentorSection.vue` on the dashboard: mentor directory when
   nothing is selected, otherwise the mentor card, thread, composer, and program
   list with adoption. Adopting refreshes the routine store.
3. `views/MentorPage.vue` at `/mentor` for `role === "mentor"`: client list,
   thread, reply composer, and program form.
4. Router: `/mentor` with `meta.requiresAuth` and `requiresRole: "mentor"`.
5. Dashboard: render `MentorSection` for `role === "user"` and a «میز کار مربی»
   link for `role === "mentor"`.
6. Tests: `stores/__tests__/mentor.spec.ts`, `components/__tests__/MentorSection.spec.ts`,
   `views/__tests__/MentorPage.spec.ts`.

## 3. Verification

```bash
# backend
cd backend
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m mypy app
.venv/Scripts/python.exe -m alembic upgrade head

# frontend
cd frontend
npx vue-tsc --noEmit
npx vitest run
npm run lint
npm run build
```

## 4. Decisions and follow-ups

- **No ADR**: this slice adds tables and endpoints inside the existing modular
  monolith; it follows ADR-0007's active-grant rule instead of introducing a new
  access model, and adds no new dependency or integration.
- **One mentor at a time** keeps consent scope explicit and matches a single
  thread on the dashboard. Multiple mentors is a later F-010/F-011 change.
- **Chat is request/response** (refresh button), not websockets; real-time
  delivery would need an ADR for transport and presence.
- **Program adoption** copies title/description into a new routine rather than
  linking scheduled items; scheduling remains F-006.
- **Mentor self-service**: mentors are created with the operator script; an
  admin verification workflow stays in F-014.
