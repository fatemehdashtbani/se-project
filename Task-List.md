# Task List

This file is the project-wide intake and delivery control. Every feature must be registered here before implementation. A task is not Ready until its `SPEC.md` and `PLAN.md` exist and are reviewed.

## Status definitions

- `Proposed` — captured, not yet specified.
- `Specifying` — SPEC/PLAN are being prepared.
- `Review` — awaiting product/architecture approval.
- `Ready` — approved and eligible for implementation.
- `In Progress` — implementation underway using TDD.
- `Blocked` — waiting for a dependency or decision.
- `In Review` — implementation complete, awaiting review/verification.
- `Done` — Definition of Done satisfied.
- `Deferred` — intentionally postponed with rationale.

## Priority definitions

- `P0` — release blocker, security, or core data integrity.
- `P1` — required for first usable release.
- `P2` — valuable, can follow initial release.
- `P3` — optional enhancement.

## Feature intake checklist

For every new feature:
- [ ] Assign a unique ID (`F-###`).
- [ ] Add the task below with priority, dependencies, status, and links.
- [ ] Create `docs/features/F-###-short-name/SPEC.md`.
- [ ] Create `docs/features/F-###-short-name/PLAN.md`.
- [ ] Define user/mentor/admin journey as applicable.
- [ ] Add testable acceptance criteria and edge cases.
- [ ] Identify data, API, authorization, consent, privacy, and operational impact.
- [ ] Create required ADR(s), or document why no ADR is needed.
- [ ] Review and approve before implementation.
- [ ] Implement Red → Green → Refactor.
- [ ] Update this list and the feature PLAN at completion.

## Initial project backlog

| ID | Feature / Workstream | Priority | Status | Dependencies | Specification | Plan |
|---|---|---:|---|---|---|---|
| F-001 | Repository foundation, tooling, configuration, CI | P0 | Done | — | `docs/features/F-001-foundation/SPEC.md` | `docs/features/F-001-foundation/PLAN.md` |
| F-002 | Login UI (mock auth) — Frontend only | P0 | Done | F-001 | `docs/features/F-002-identity/SPEC.md` | `docs/features/F-002-identity/PLAN.md` |
| F-003 | Role-based access control - User / Mentor / Admin | P0 | Done | F-019 | `docs/features/F-003-rbac/SPEC.md` | `docs/features/F-003-rbac/PLAN.md` |
| F-004 | User profile, onboarding, time-zone preference | P0 | Done | F-019 | `docs/features/F-004-profile/SPEC.md` | `docs/features/F-004-profile/PLAN.md` |
| F-005 | Routine CRUD — create, edit, archive, delete | P0 | Proposed | F-003, F-004 | `docs/features/F-005-routine-crud/SPEC.md` | `docs/features/F-005-routine-crud/PLAN.md` |
| F-006 | Routine scheduling — recurring patterns (daily/weekly/monthly) | P0 | Proposed | F-005 | `docs/features/F-006-routine-scheduling/SPEC.md` | `docs/features/F-006-routine-scheduling/PLAN.md` |
| F-007 | Check-in tracking — mark done/not done with optional note | P0 | Proposed | F-006 | `docs/features/F-007-check-in/SPEC.md` | `docs/features/F-007-check-in/PLAN.md` |
| F-008 | Dashboard, streaks, and analytics | P1 | Proposed | F-007 | `docs/features/F-008-dashboard/SPEC.md` | `docs/features/F-008-dashboard/PLAN.md` |
| F-009 | Reminders and notifications — email + Android push (FCM) | P1 | Proposed | F-007 | `docs/features/F-009-notifications/SPEC.md` | `docs/features/F-009-notifications/PLAN.md` |
| F-010 | Mentor discovery — browse and select a mentor | P1 | Proposed | F-003 | `docs/features/F-010-mentor-discovery/SPEC.md` | `docs/features/F-010-mentor-discovery/PLAN.md` |
| F-011 | Mentor access — consent-based, revocable | P0 | Proposed | F-003, F-005 | `docs/features/F-011-mentor-access/SPEC.md` | `docs/features/F-011-mentor-access/PLAN.md` |
| F-012 | Mentor messaging and comments | P1 | Proposed | F-011 | `docs/features/F-012-mentor-messaging/SPEC.md` | `docs/features/F-012-mentor-messaging/PLAN.md` |
| F-013 | Subscription plans (Free / Paid) and plan-limit enforcement | P1 | Proposed | F-003 | `docs/features/F-013-subscriptions/SPEC.md` | `docs/features/F-013-subscriptions/PLAN.md` |
| F-014 | Admin panel — user management, plan management, monitoring | P1 | Proposed | F-003, F-013 | `docs/features/F-014-admin/SPEC.md` | `docs/features/F-014-admin/PLAN.md` |
| F-015 | Android app — notifications, check-ins, routine viewing | P1 | Proposed | F-007, F-009 | `docs/features/F-015-android/SPEC.md` | `docs/features/F-015-android/PLAN.md` |
| F-016 | Team / group routines | P2 | Proposed | F-007 | `docs/features/F-016-team-routines/SPEC.md` | `docs/features/F-016-team-routines/PLAN.md` |
| F-017 | Production hardening — backup/restore, observability, security review | P0 | Proposed | F-001–F-014 | `docs/features/F-017-production-readiness/SPEC.md` | `docs/features/F-017-production-readiness/PLAN.md` |
| F-018 | Upgrade frontend dependencies (ESLint 9, Vitest 2) to resolve audit warnings | P2 | Proposed | — | — | — |
| F-019 | Identity Backend — Registration, JWT sessions (Hybrid), Argon2 | P0 | Done | F-001 | `docs/features/F-019-identity-backend/SPEC.md` | `docs/features/F-019-identity-backend/PLAN.md` |
| F-023 | Frontend Auth Integration - Pinia store, API client, login wiring, route guard | P0 | Done | F-002, F-019 | `docs/features/F-023-frontend-auth/SPEC.md` | `docs/features/F-023-frontend-auth/PLAN.md` |
| F-025 | Frontend registration UI - `/register` form with auto-login | P0 | Done | F-019, F-023 | `docs/features/F-025-register-ui/SPEC.md` | `docs/features/F-025-register-ui/PLAN.md` |
| F-026 | Auth UI redesign (split-screen, dark theme) and user profile fields | P0 | Done | F-019, F-025 | `docs/features/F-026-auth-redesign/SPEC.md` | `docs/features/F-026-auth-redesign/PLAN.md` |
| F-028 | Profile & dashboard polish (icon, greeting, editable profile, mock password change, back button) | P2 | Done | F-019, F-026 | `docs/features/F-028-profile-dashboard-polish/SPEC.md` | `docs/features/F-028-profile-dashboard-polish/PLAN.md` |
| F-029 | Fixed bottom navigation across authenticated pages and dedicated logout icon | P2 | Done | F-023, F-026 | `docs/features/F-029-bottom-navigation/SPEC.md` | `docs/features/F-029-bottom-navigation/PLAN.md` |
| F-005 | Routine CRUD - model, endpoints, ownership, store and dashboard UI | P1 | Done | F-019, F-003 | `docs/features/F-005-routine-crud/SPEC.md` | `docs/features/F-005-routine-crud/PLAN.md` |
| F-030 | Admin panel UI shell — role-gated RTL sidebar layout, 403 page, role-aware auth redirects (reference-based) | P1 | Done | F-003, F-023, F-029 | `docs/features/F-030-admin-panel-shell/SPEC.md` | `docs/features/F-030-admin-panel-shell/PLAN.md` |

## Current sprint

No sprint has been committed yet. Select work only from tasks whose status is `Ready`.

## Change log

| Date | Change |
|---|---|
| 2026-11-19 | Backlog corrected: F-002 retitled to "Login UI (mock auth) — Frontend only"; F-019 (Identity Backend) added as P0/Ready; F-003 and F-004 dependencies moved from F-002 to F-019. |
| 2026-11-19 | F-002 login UI implemented (TDD, 8 component tests) and marked Done; email-format validation added. Visual layout verification deferred to Playwright E2E in F-017. |
| 2026-11-19 | F-019 closed as Done (all 8 FRs implemented, 18 backend tests green); title corrected to drop the deferred Password Reset scope. F-023 (Frontend Auth Integration) added as P0/Approved with SPEC and PLAN. |
| 2026-11-20 | F-023 closed as Done: Pinia auth store, `fetch` client with error-envelope mapping, login/logout wiring, router guard, boot-time session hydration, and Persian error messages (25 frontend tests green, live smoke test through the Vite proxy). |
| 2026-11-20 | F-003 (RBAC) SPEC/PLAN approved and status moved to Approved; `/api/v1/healthz` alias added and logout redirect hardened against network failure. |
| 2026-11-20 | F-003 closed as Done: `require_role` (`Literal` role, `FORBIDDEN` 403), test-only admin router, `create_admin.py` promote-by-email script, and frontend `UserRole` union (8 backend RBAC/service tests; 27 backend and 26 frontend tests green). |
| 2026-11-22 | F-004 (Profile and Timezone UI) SPEC/PLAN approved; RED tests added for `authStore.updateTimezone()` and `ProfilePage.vue`. |
| 2026-11-22 | F-004 closed as Done: profile page with curated+injected IANA list, `updateTimezone` store action, guarded `/profile` route, Dashboard link, and Persian success/error messages (35 frontend tests green; timezone round-trip verified live through the Vite proxy). |
| 2026-11-22 | F-025 closed as Done: `/register` view with client validation and Persian errors, `authStore.register()` (register → login → me under one `isLoading` guard), public `/register` route, login↔register links, extracted `shared/utils/validation.ts`, and the first Playwright E2E suite covering register → dashboard → profile → timezone → reload → logout against a throwaway `e2e.db`. |
| 2026-11-24 | Mobile login (`identifier` = email or phone, case/space normalized, ambiguous phones rejected) and the mocked `POST /api/v1/auth/forgot-password` endpoint; dark-theme dashboard/profile with the profile icon, read-only profile fields, and a new `/forgot-password` page. Not yet covered by a dedicated F-### SPEC/PLAN. |
| 2026-11-23 | F-005 backend GREEN: routine schemas, owner-scoped service, and `/api/v1/routines` routes (create/list/get/partial update/soft delete, foreign ids → 404 `ROUTINE_NOT_FOUND`, paginated list). The 14 previously RED tests now pass; backend suite is 48 passed. Frontend store and dashboard UI remain for F-005. |
| 2026-11-23 | F-026 backfilled as Done: SPEC/PLAN written after the fact for the professor-requested auth redesign — `User` profile fields (`username`, `first_name`, `last_name`, `phone_number`) with migration `c7d18ab07c7d`, required registration fields, and the RTL split-screen dark auth layout (`AuthLayout.vue`). |
| 2026-11-24 | F-028 backfilled as Done: SPEC/PLAN recorded for the profile/dashboard polish (profile icon, dynamic greeting, editable profile, mock password change, dashboard back button). |
| 2026-11-24 | F-005 completed with `useRoutineStore` (fetch/create/delete through `/api/v1/routines`) and the dashboard routine list with Persian empty state, inline create form, and delete controls; frontend store/component tests added. |
| 2026-11-24 | F-029 closed as Done: shared fixed `BottomNav` on the dashboard and profile routes, dedicated `LogoutIcon`, and logout redirect tests. |
| 2026-11-24 | F-030 closed as Done: admin UI shell adapted from the reference project — role-gated `/admin` routes, RTL dark `AdminLayout`/`AdminSidebar`, placeholder admin pages, Persian 403 page, `panelPath` role-aware redirects on the existing Persian login/register pages. Backend admin management (F-014) remains out of scope. |
| 2026-11-19 | F-001 marked Done (scaffold, lint, type-check, and tests pass). F-002 login UI SPEC/PLAN approved and marked Ready. F-018 added to track remaining frontend dependency upgrades required to clear `npm audit` critical/high findings. |
| 2026-11-18 | Initial backlog and feature-intake workflow created (v2.0 — F-### IDs). |
