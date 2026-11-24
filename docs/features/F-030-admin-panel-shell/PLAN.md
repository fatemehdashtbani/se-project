# Implementation Plan — F-030 Admin Panel UI Shell

- Status: Done
- Related SPEC: `SPEC.md`
- Closure note: implemented under the explicit user request to adapt the reference admin panel and bring the app up; the full admin management feature F-014 remains Proposed.

## 1. Ordered implementation steps
1. Register F-030 in `Task-List.md` with links to SPEC/PLAN.
2. **RED:** add tests for `panelPath`, the admin guard in the router, the admin shell/sidebar/landing/403 pages, and role-aware redirects in login/register.
3. **GREEN:** add `shared/utils/paths.ts`; add `AdminLayout.vue`, `AdminSidebar.vue`, `AdminHome.vue`, `AdminSectionPage.vue`, `ForbiddenPage.vue`; wire the routes and guard; add the auth-page headings and redirects.
4. **Refactor:** keep all role checks in the router + server session; remove duplicated logout logic from the sidebar.
5. Run the full unit suite, lint, and type-check; start the Vite dev server and report the URL.

## 2. ADR decision
No ADR required: the existing ADR-0006 role model is reused unchanged, no backend contract or data store is introduced, and the placeholder pages perform no admin operations.

## 3. Migration / rollback
None — frontend-only files. Rollback is a single revert of this feature's commit; no database migration or environment variable is involved.

## 4. Completion checklist
- [x] F-030 registered with SPEC/PLAN.
- [x] Unit, router, and component tests pass.
- [x] Lint and type-check clean.
- [x] Admin shell visible at `/admin` for the admin role only.
- [x] Full F-014 admin management explicitly deferred.
