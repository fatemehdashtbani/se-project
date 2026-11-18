# Delivery Roadmap

This roadmap proposes an incremental path from an empty repository to a
production-ready first release. It is a sequencing recommendation, not
authorization to skip feature SPEC/PLAN approval.

## Phase 0 — Engineering Foundation

**Tasks:** F-001
**Outcome:** Reproducible development environment and quality gates.

- Repository layout, frontend/backend bootstraps.
- Formatting, linting, type checking, test runners.
- CI pipeline (GitHub Actions).
- Environment configuration and secret handling.
- SQLite local configuration and PostgreSQL service for integration tests.
- Alembic baseline and health endpoints.
- Initial ADRs.

**Exit gate:** A clean clone can run frontend/backend and all baseline checks
in documented steps.

## Phase 1 — Identity and Access Control

**Tasks:** F-002, F-003, F-004
**Outcome:** Secure accounts, roles, and time-zone-aware profiles.

- Registration, email verification, login/logout, password reset.
- Role-based access control (User / Mentor / Admin) with ownership checks.
- User profile and IANA time-zone preference.
- Object-level authorization tests.

**Exit gate:** Role and ownership tests prove users cannot access other users'
resources; timezone changes are recorded correctly.

## Phase 2 — Routine Core

**Tasks:** F-005, F-006, F-007
**Outcome:** Users can create routines, define recurrence, and check in.

- Routine CRUD (create, edit, archive, soft-delete).
- Recurrence engine (daily, specific weekdays, N-times-per-week, monthly).
- Check-in with status (done/skipped) and optional note.
- (routine_id, local_date) unique constraint enforced on SQLite and
  PostgreSQL.
- Idempotency key on check-in creation.

**Exit gate:** A user can create a routine, check in today, and cannot create
a second check-in for the same local day. Timezone and DST boundary tests
pass.

## Phase 3 — Insights and Notifications

**Tasks:** F-008, F-009
**Outcome:** Users can review progress and receive reminders.

- Streaks (computed from stored local_date), completion-rate dashboards.
- Calendar heatmap and trend charts.
- Reminder scheduling and dispatch via FastAPI BackgroundTasks.
- Notification preferences and in-app notification center.

**Exit gate:** Reminders fire at the user's local time; DST and
timezone-change cases produce the correct reminder time; notification
failure does not roll back a check-in.

## Phase 4 — Mentor Layer

**Tasks:** F-010, F-011, F-012
**Outcome:** Consent-based mentor collaboration.

- Mentor profiles and discovery.
- MentorGrant (consent) grant/revoke with explicit scope.
- Mentor read access gated by active consent on every request.
- Mentor comments and direct messages.
- Audit logging for consent events.

**Exit gate:** Mentor access is denied without an active grant; revoking a
grant blocks the very next request; all consent changes are audited.

## Phase 5 — Monetization and Administration

**Tasks:** F-013, F-014
**Outcome:** Plan management and admin operations.

- Subscription plans (Free/Paid) with server-enforced limits.
- Plan changes and downgrade behavior (no data deletion).
- Admin panel for user/mentor/plan management.
- Audit log viewer and operational metrics.

**Exit gate:** Plan-limit bypass attempts are rejected server-side; admin
actions are audited; existing data survives plan downgrade.

## Phase 6 — Android Client

**Tasks:** F-015
**Outcome:** End users can check in and receive push notifications on
Android.

- Android app (tech TBD via ADR-0012) consuming the same /api/v1 API.
- Push notifications (FCM) for routine reminders.
- Consent, plan-limit, and ownership checks are not bypassed by the native
  client.

**Exit gate:** A user can check in from Android; push notifications arrive
at the correct local time; no client can bypass consent or plan limits.

## Phase 7 — Team / Group Routines

**Tasks:** F-016 (optional, P2)
**Outcome:** Shared routines for groups.

Each feature requires its own SPEC/PLAN and ADR; do not couple core routine
correctness to group semantics.

## Phase 8 — Production Readiness

**Tasks:** F-017
**Outcome:** Deployable and supportable service.

- Security review and dependency scanning.
- Load/performance testing.
- PostgreSQL migration validation.
- Backup and restore exercise.
- Monitoring, alerting, incident and rollback runbooks.
- Privacy, terms, retention, and operational review.

**Release gate:** All P0 tasks Done, no unresolved critical
security/data-integrity issues, restore test successful, and product
decisions resolved.
