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
| F-003 | Role-based access control — User / Mentor / Admin | P0 | Proposed | F-019 | `docs/features/F-003-rbac/SPEC.md` | `docs/features/F-003-rbac/PLAN.md` |
| F-004 | User profile, onboarding, time-zone preference | P0 | Proposed | F-019 | `docs/features/F-004-profile/SPEC.md` | `docs/features/F-004-profile/PLAN.md` |
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
| F-023 | Frontend Auth Integration — Pinia store, API client, login wiring, route guard | P0 | Approved | F-002, F-019 | `docs/features/F-023-frontend-auth/SPEC.md` | `docs/features/F-023-frontend-auth/PLAN.md` |

## Current sprint

No sprint has been committed yet. Select work only from tasks whose status is `Ready`.

## Change log

| Date | Change |
|---|---|
| 2026-11-19 | Backlog corrected: F-002 retitled to "Login UI (mock auth) — Frontend only"; F-019 (Identity Backend) added as P0/Ready; F-003 and F-004 dependencies moved from F-002 to F-019. |
| 2026-11-19 | F-002 login UI implemented (TDD, 8 component tests) and marked Done; email-format validation added. Visual layout verification deferred to Playwright E2E in F-017. |
| 2026-11-19 | F-019 closed as Done (all 8 FRs implemented, 18 backend tests green); title corrected to drop the deferred Password Reset scope. F-023 (Frontend Auth Integration) added as P0/Approved with SPEC and PLAN. |
| 2026-11-19 | F-001 marked Done (scaffold, lint, type-check, and tests pass). F-002 login UI SPEC/PLAN approved and marked Ready. F-018 added to track remaining frontend dependency upgrades required to clear `npm audit` critical/high findings. |
| 2026-11-18 | Initial backlog and feature-intake workflow created (v2.0 — F-### IDs). |
