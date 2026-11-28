# F-037 — Implementation plan

## Ordered steps

1. Extend the data model: `User.is_active`, `User.is_banned`, `HabitCategory`,
   `RoutineTemplate`, `Broadcast`, `SystemLog`; add migration `b3c1d7e9a2f4`.
2. Enforce account controls in `authenticate_user`, `rotate_refresh_token`, and
   `get_current_user` (`ACCOUNT_DISABLED`).
3. Add `app/services/admin.py` for dashboard aggregation, account actions,
   mentorship supervision, content CRUD and log reads. Every mutation calls
   `record_log`.
4. Add `app/api/routes/admin.py` (admin-gated) with pagination and filters.
5. Add request middleware that records failed `/api/v1/*` responses; skipped for
   in-memory test databases.
6. Frontend: install `element-plus` + icons, register the Persian locale, add
   the purple/white theme (`assets/styles/admin.css`).
7. Rewrite `AdminLayout`/`AdminSidebar` with `el-menu`, and build the five views:
   `AdminHome`, `AdminUsers`, `AdminMentors`, `AdminContent`, `AdminSystem`.
8. Add `stores/admin.ts` for the API surface and update the router (legacy
   `/admin/mentor-applications` and `/admin/plans` redirect to the new sections).
9. Update tests: admin API integration tests, admin store tests, sidebar and
   dashboard component tests; add the jsdom storage setup shim.

## Tests first / verification

- `backend/tests/api/test_admin.py`: authorization, dashboard counters, ban and
  activation enforcement, temporary password login, template/category CRUD and
  audit entries, broadcast listing.
- Frontend: `stores/__tests__/admin.spec.ts`, `AdminSidebar.spec.ts`,
  `AdminPages.spec.ts`.
- Commands: `ruff check`, `mypy app`, `pytest`, `npm run type-check`,
  `npm run test:unit`, `npm run build`.

## Migration and rollback

`alembic upgrade head` adds the columns and tables; `alembic downgrade -1`
drops them and the two user columns. Only additive changes, so no data loss on
upgrade.

## ADR

No new ADR: the feature adds CRUD tables and a middleware behind existing
architecture (modular monolith, service/route split, RBAC dependency). It does
not change system boundaries, consistency strategy, or integrations.

## Completion checks

- All admin routes 401/403 correctly.
- No password or token value reaches the log.
- `Task-List.md` updated to `Done` with a change-log entry.
