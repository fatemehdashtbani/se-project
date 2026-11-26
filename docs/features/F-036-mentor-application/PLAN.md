# F-036 — Implementation plan

## 1. Data and backend

1. `MentorApplication` in `app/infrastructure/db/models.py`: one row per account,
   `status` default `pending`, `reviewed_at`/`reviewed_by` for the decision, and
   an index on `(status, created_at)`.
2. Migration `f1a2b3c4d5e6` (revises `e7b3f9a2c4d6`) creating
   `mentor_applications`; downgrade drops the indexes and the table.
3. `app/schemas/mentor_application.py`: create payload with trimming/limits,
   owner response, `MyMentorApplicationResponse`, and the admin item carrying the
   applicant's name and email.
4. `app/services/mentor_applications.py`: `get_application`,
   `submit_application` (create or reset to pending, refuse mentors),
   `list_applications(status)`, `approve_application` (role + profile upsert),
   `reject_application`, and `_get_pending` guarding repeated reviews.
5. `app/api/routes/mentor_applications.py`: applicant routes plus an admin
   router under `/api/v1/admin/mentor-applications`, registered in `app/main.py`;
   `require_role("user")` for submission and `require_role("admin")` for review.
6. Tests in `backend/tests/api/test_mentor_applications.py` (Red first): auth,
   submit/resubmit, admin-only access, approval promotion and directory entry,
   rejection and resubmission, status filtering, validation, unknown ids.

## 2. Frontend

1. `stores/mentorApplication.ts`: typed application, admin item and status label
   map, plus `fetchMine`, `submit`, `fetchApplications`, `approve`, `reject`.
2. `views/BecomeMentorPage.vue` at `/become-a-mentor`: state banner
   (pending/approved/rejected), form (expertise, biography, documents), Persian
   validation, success notice, and the mentor-account short circuit.
3. `views/admin/AdminMentorApplicationsPage.vue` at
   `/admin/mentor-applications`: queue, empty/loading/error states, and the
   approve/reject actions.
4. Dashboard section «همکاری به عنوان مربی» for `role === "user"` with the
   button «درخواست همکاری به عنوان مربی» and the current status; the store is
   loaded after mount without blocking routines.
5. Router: `/become-a-mentor` (`requiresAuth`) and the admin child route; add
   «درخواست‌های مربیگری» to `AdminSidebar`.
6. Tests: `BecomeMentorPage.spec.ts`, `AdminMentorApplicationsPage.spec.ts`,
   the dashboard link/status cases, the sidebar link list, and the login
   role-mismatch cases.

## 3. Verification

```bash
cd backend
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m mypy app
.venv/Scripts/python.exe -m alembic upgrade head

cd frontend
npx vue-tsc --noEmit
npx vitest run
npm run lint
npm run build
```

## 4. Decisions and follow-ups

- **No ADR**: the change adds one table and two endpoint groups inside the
  existing modular monolith, reuses the RBAC dependency and the F-035 profile
  table, and introduces no dependency or external integration.
- **Documents are typed text** (link or description) instead of uploads: file
  storage, type/size validation and retention need their own specification, so
  the MVP collects evidence as text.
- **One row per account** keeps the latest decision and resubmission a single
  lookup; no application history table is introduced.
- **No withdrawal**: once approved, demoting a mentor is an administrative
  operation outside this slice.
- **Audit trail deferred**: privileged mutations should produce audit entries
  (AGENTS §10); the platform has no audit table yet, so this is tracked with the
  admin work in F-014.
- Login changes in the same request (role-mismatch message instead of the 403
  page, mobile artwork fixed behind the form sheet) are UI corrections recorded
  in the Task-List change log rather than part of this feature.
