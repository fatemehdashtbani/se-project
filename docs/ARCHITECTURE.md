# Software Architecture Document (SAD)

**Product:** Routine Manager — Online Routine & Habit Management Platform
**Status:** Initial architecture baseline
**Version:** 1.0
**Date:** 2026-11-18

## 1. Purpose and scope

This document describes the logical and deployment architecture for an online
routine-management platform where individuals create and track routines/habits,
mentors support users with explicit revocable consent, and administrators
operate subscription plans and platform governance.

The first release targets a single deployable product. The architecture
deliberately starts as a modular monolith. Microservices are not a
first-release requirement.

## 2. Architecture drivers

1. Correct check-in semantics across time zones: at most one active check-in per
   routine per user's local calendar day.
2. Correct streak computation across DST transitions and user time-zone changes.
3. Support three roles: User, Mentor, Platform Administrator.
4. Enforce consent-based mentor access: mentors see user data only when an
   active consent record exists.
5. Enforce plan limits (Free/Paid) server-side; never trust the client.
6. Enable iterative delivery with TDD and documented feature specifications.
7. Keep local development easy with SQLite while using PostgreSQL as production
   source of truth.
8. Maintain clear seams for future notification channels (email, Android push)
   and payments.
9. Protect personal data and enforce server-side authorization.

## 3. Technology baseline

| Concern | Choice | Notes |
|---|---|---|
| Frontend (web) | Vue 3 + TypeScript + Vite | Composition API, Vue Router, Pinia |
| Frontend UI | FarsiUI-inspired components (reference + manual port) | See docs/FARSIUI_GUIDE.md |
| Mobile (Android) | TBD — see ADR-0004 | Flutter / React Native / Kotlin |
| Backend | FastAPI + Python 3.12+ | Versioned REST API |
| Validation | Pydantic v2 | Request/response contracts |
| ORM | SQLAlchemy 2.x (async) | Typed mappings and explicit transactions |
| Migrations | Alembic | All schema changes versioned |
| Local DB | SQLite | Development and fast tests only |
| Production DB | PostgreSQL | Authoritative transactional database |
| Backend tests | pytest + pytest-asyncio + httpx | Unit, integration, contract, time-zone |
| Frontend tests | Vitest + Vue Test Utils | Component and composable tests |
| E2E | Playwright | Critical user journeys |
| API contract | OpenAPI | FastAPI-generated, reviewed |
| CI | GitHub Actions | Lint, type-check, tests, migration checks |
| Background work (MVP) | FastAPI BackgroundTasks | Durable queue via ADR when needed |
| Cache/broker | Not required initially | Add only for measured need |

Suggested libraries (subject to ADR or dependency review): Vue Router, Pinia,
a maintained form/validation library (zod + vee-validate), and a maintained
date/time library with IANA timezone support. Do not hand-roll timezone
conversion.

## 4. Architectural style

### 4.1 Modular monolith

One backend application and one primary relational database, internally divided
into domain modules. This provides straightforward transactions and deployment
while preserving boundaries for future extraction.

### 4.2 Backend layers

- **API layer:** FastAPI routers, authentication dependencies, request parsing,
  response serialization.
- **Application layer:** use cases, orchestration, transaction boundaries,
  authorization checks (including consent).
- **Domain layer:** entities, value objects, policies, routine and check-in
  invariants.
- **Infrastructure layer:** SQLAlchemy repositories, email/push adapters,
  worker, external clients.

Domain modules must not import FastAPI or vendor-specific infrastructure.
Infrastructure implements interfaces required by application/domain layers.

### 4.3 Suggested repository structure

routine-manager/
├── AGENTS.md
├── Task-List.md
├── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── router/
│   │   ├── modules/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── services/api/
│   │   └── stores/
│   └── tests/
├── mobile/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/
│   │   ├── modules/
│   │   │   ├── identity/
│   │   │   ├── routines/
│   │   │   ├── checkins/
│   │   │   ├── mentors/
│   │   │   ├── subscriptions/
│   │   │   ├── admin/
│   │   │   └── notifications/
│   │   ├── infrastructure/
│   │   └── main.py
│   ├── migrations/
│   └── tests/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SRS.md
│   ├── ROADMAP.md
│   ├── FARSIUI_GUIDE.md
│   ├── adr/
│   ├── features/
│   └── templates/
└── .github/workflows/

Note: no Docker or Kubernetes for local development per project constraints.

## 5. Context and main components

User Browser        Mentor Browser        Admin Browser        Android App
     |                    |                     |                    |
     +--------------------+---------------------+--------------------+
                              |
                     Vue 3 SPA / Android
                              |
                        HTTPS / REST
                              |
                          FastAPI
                              |
     +------------------------+-------------------------+
     |            |            |           |           |
  Identity    Routine     CheckIn    Mentor       Subscription
     |        + Schedule       |      + Consent          |
     |            |            |           |           |
  User/Profile   |         CheckIn       Comment       Plan/Limit
     |            |         History       Message          |
     +------------+------------+------------+------------+
                              |
                     SQLAlchemy / Unit of Work
                              |
                    PostgreSQL (production)
                    SQLite (local development)
                              |
                  BackgroundTasks / Outbox
                    |             |              |
                  Email      FCM Push       (Future:
                                            Payments)

## 6. Domain model overview

Core entities and relationships (final schema is refined in feature
specifications and ADRs):

- **User:** identity, email, password hash, status, locale, IANA timezone,
  timestamps.
- **Role / Permission:** authorization capabilities (User/Mentor/Admin).
- **UserProfile:** display name, bio, preferences, onboarding state.
- **Routine:** user-owned habit/task, title, target frequency, schedule
  reference, active state, plan-tier snapshot.
- **RoutineSchedule:** recurring pattern (daily/weekly/monthly, day-of-week,
  day-of-month, start/end local dates).
- **CheckIn:** per routine per local_date, UTC instant, IANA timezone at
  check-in, local_date YYYY-MM-DD, status (done/skipped), optional note.
  Unique constraint on (routine_id, local_date).
- **MentorProfile:** public profile, bio, specialties, verification state,
  default timezone.
- **MentorGrant:** consent record between user and mentor with granted_at and
  revoked_at; must be active (not revoked) for mentor access.
- **MentorComment:** mentor's comment on a user's routine or check-in, tied to
  an active grant.
- **MentorMessage:** 1:1 message thread between user and mentor, tied to an
  active grant.
- **Plan:** Free/Paid tier with limits (e.g., max active routines).
- **Subscription:** user's current plan, start/end, billing reference.
- **Notification / OutboxMessage:** queued side effects (email, push) and
  delivery state.
- **AuditLog:** actor, action, target, timestamp, request correlation, redacted
  metadata.

Use explicit foreign keys, unique constraints, check constraints, indexes, and
deletion policies. Prefer deactivation/soft deletion for records referenced by
check-ins and audit.

## 7. Identity and authorization

Use role-based access control plus resource ownership checks plus consent
checks.

- **User:** manage own profile, own routines, own check-ins, own subscription;
  grant/revoke mentor consent.
- **Mentor:** read a user's routines, check-ins, and progress only when an
  active MentorGrant exists; write comments and messages in that scope; manage
  own mentor profile.
- **Administrator:** access platform administration according to explicit
  permission scopes; actions are audited.
- **Public visitor:** read only published mentor profiles.

A role is not sufficient by itself. Every protected endpoint must check role
AND ownership AND (for mentor access) active consent AND (for plan-gated
resources) plan limits.

Authentication strategy (cookie session vs bearer/refresh token) must be
selected in an ADR before implementation. For browser-first deployment, secure
HttpOnly cookies are a strong default; include CSRF protection and SameSite
policy. Android may use bearer/refresh tokens; define both in ADR-0005.

## 8. Routine and time correctness

### 8.1 Time model

- Persist actual instants (check-in time, reminder schedule) as UTC timestamps.
- Persist the user's IANA timezone on the user record and, for each check-in,
  the timezone at the time of check-in (denormalized).
- The "local day" of a check-in is local_date (YYYY-MM-DD) computed using the
  user's timezone at check-in time.
- Streaks are computed by walking consecutive local_date values, not by adding
  fixed 24-hour increments.
- DST transitions must not break streaks: a 23-hour or 25-hour day still counts
  as one local day.
- When a user changes their timezone, prior check-ins retain their original
  local_date and timezone; new check-ins use the new timezone.

### 8.2 Check-in rule

A user may have at most one active check-in per routine per local calendar day,
enforced by a database unique constraint on (routine_id, local_date). This is
the routine-tracking analogue of "no overlapping bookings."

The check-in use case must:
1. Resolve the user's current IANA timezone.
2. Compute local_date from the UTC instant.
3. Reject (409) if an active check-in already exists for the same
   (routine_id, local_date).
4. Persist the UTC instant, the IANA timezone, and the local_date atomically.

SQLite supports the same unique constraint. PostgreSQL is authoritative for
production validation. Run the time-zone/conflict suite against PostgreSQL in
CI when touching persistence.

### 8.3 Recurring schedules

- Routine schedules are defined in the user's local time zone (day-of-week,
  day-of-month).
- The system must not assume that UTC Monday equals local Monday.
- Schedule matching is evaluated using each check-in's local_date and the
  routine's recurrence rule.

## 9. Check-in transaction and duplicate prevention

The check-in use case must re-check the local-day uniqueness inside one
database transaction.

Recommended approach (portable to SQLite and PostgreSQL):
- Compute local_date from the UTC check-in instant and the user's IANA timezone.
- Attempt the INSERT with a unique constraint on (routine_id, local_date).
- If the constraint fires, return HTTP 409 with a stable error code and a
  localizable user-facing message.
- Add an idempotency key unique per user/request scope to make retries safe.
- Commit check-in and outbox notification records atomically.
- Dispatch reminders/notifications only after commit.

SQLite enforces UNIQUE(routine_id, local_date) identically to PostgreSQL for
this use case, so both are viable for fast tests. PostgreSQL remains
authoritative for production.

## 10. Routine lifecycle

Initial routine states:
- ACTIVE — user can check in.
- ARCHIVED — no new check-ins; history retained.
- DELETED — soft-deleted; hidden but retained for audit/history.

Initial check-in states:
- DONE
- SKIPPED

State transitions must be explicit and validated by a domain policy. Preserve
history; do not silently overwrite status.

## 11. Database strategy

### 11.1 SQLite

- Default local development configuration.
- Useful for fast tests of portable business logic and basic persistence.
- Enable foreign-key enforcement for every connection.
- Use migrations in development just as in production.
- The (routine_id, local_date) unique constraint is portable and enforced on
  SQLite.
- Do not rely on SQLite for PostgreSQL-specific behavior in production.

### 11.2 PostgreSQL

- Required for production.
- Required for authoritative time-zone and concurrency tests.
- Required for migration validation.
- Use connection pooling appropriate to deployment.
- Define backup, restore, retention, and upgrade procedures before production.

### 11.3 ORM and migrations

SQLAlchemy 2.x is the persistence abstraction. Alembic manages schema
evolution. Keep domain logic independent of SQLAlchemy where practical. Never
modify a released migration; add a new migration. Review generated migrations
manually.

## 12. API design

- Base path: /api/v1.
- REST conventions and resource-oriented endpoints.
- OpenAPI is the API contract.
- Use Pydantic schemas for input/output.
- Standard error structure with stable machine-readable code, human-readable
  message (localizable), and optional field errors.
- Pagination for list endpoints.
- Use idempotency keys on check-in creation and other retry-sensitive commands.
- Use UTC ISO 8601 instants; always include the IANA timezone where local-day
  semantics matter.

Indicative endpoint groups:
- /auth/*, /users/me, /users/me/timezone
- /routines, /routines/{routine_id}, /routines/{routine_id}/schedule
- /routines/{routine_id}/check-ins, /check-ins
- /mentors, /mentors/{mentor_id}, /mentors/me
- /mentors/{mentor_id}/grants (consent grant/revoke)
- /mentors/me/clients, /mentors/me/clients/{user_id}/routines (requires active grant)
- /mentors/me/clients/{user_id}/comments
- /subscriptions/plans, /subscriptions/me
- /admin/users, /admin/plans, /admin/audit-logs
- /notifications (user-facing list of recent notifications)

Exact endpoint contracts belong in feature SPECs.

## 13. Frontend architecture

Vue 3 + TypeScript SPA. Organize by business module rather than only by
technical file type. Use typed API clients. Keep server state distinct from
ephemeral UI state. Use route guards for UX but always enforce authorization on
the backend.

Required UX states: loading, empty, validation error, server error, success,
and retry. Accessibility target WCAG 2.2 AA as a product goal.

Android app (tech TBD) consumes the same /api/v1 API. It must NOT bypass
consent, plan-limit, or ownership checks by being a "native" client.

## 14. Notifications and background work

- Email notifications: account verification, password reset, mentor consent
  grant/revoke, subscription change.
- Android push notifications (FCM): routine reminders at the user's local time.
- For MVP (no Redis): use FastAPI BackgroundTasks for dispatch. When scale
  demands a durable queue, introduce one behind an approved ADR.
- Use an outbox pattern for reliable delivery when a committed check-in must
  trigger a reminder.
- Retries must be bounded and observable.
- Scheduled reminders need deduplication and timezone-safe scheduling (handle
  DST gaps and repeated local times).

## 15. Payments and external integrations

Subscription billing is deferred to a future ADR when paid plans go live.

- Use a payment provider adapter with hosted/tokenized payment UI.
- Never store card numbers or CVV.
- Treat signed webhooks as authoritative for asynchronous payment status.
- Make webhook processing idempotent.
- Define refund and cancellation policy before enabling payment.

## 16. Security, privacy, and compliance

Threat model at minimum: account takeover, privilege escalation, insecure
direct object references, mentor access without consent, plan-limit bypass,
brute force, CSRF/XSS, injection, webhook spoofing/replay, secret leakage, and
personal-data overexposure.

Controls:
- Secure password hashing (Argon2id), email verification, password reset, rate
  limiting.
- Server-side RBAC + ownership + consent + plan-limit checks.
- Secure cookies/CSRF controls or a documented token architecture (both browser
  and Android).
- TLS in transit and encrypted backups where available.
- Secrets management.
- Audit logs for role changes, consent grants/revocations, plan changes, and
  admin actions.
- Data minimization, retention/deletion workflows, and export capability.
- Privacy notice and terms reviewed before launch.
- A formal legal review is required before making compliance claims.

## 17. Non-functional targets

Initial targets to validate and adjust with actual usage:

- Availability: 99.5% monthly in first production stage; raise only when
  justified.
- Performance: p95 under 500 ms for ordinary read/write endpoints; reminder
  dispatch measured separately.
- Correctness: zero duplicate active check-ins per routine per local day; zero
  streak breaks due to DST.
- Security: no known critical/high vulnerabilities at release.
- Recovery: define RPO/RTO before production; initial proposal RPO <= 24h,
  RTO <= 8h.
- Accessibility: WCAG 2.2 AA.
- Maintainability: automated tests, migrations, linting, type checks, and
  documented operations.

These are proposed engineering targets, not measured guarantees.

## 18. Deployment view

- Static frontend hosting or web server/CDN.
- FastAPI app behind reverse proxy/load balancer.
- PostgreSQL (production).
- A background worker for outbox and reminders (FastAPI BackgroundTasks
  initially; scale-up path via ADR).
- SMTP/email provider and FCM credentials.
- Centralized logs and basic metrics.
- Backup storage separate from primary DB.

No Docker or Kubernetes for local development (per project constraints).
Local run uses venv + npm directly. Containerization may be revisited for
deployment via ADR.

Build CI stages for lint/type-check/test/build/migration validation.

## 19. Architecture risks

| Risk | Impact | Mitigation |
|---|---|---|
| Duplicate check-ins across time zones | High | Unique constraint (routine_id, local_date), timezone at check-in, boundary tests |
| DST/timezone errors in streaks or reminders | High | IANA timezone model, explicit DST policy, boundary tests |
| Mentor accesses user data without consent | Critical | Consent check on every read, audit log, deny-by-default, tests |
| Plan-limit bypass by client manipulation | High | Server-side enforcement, tests that simulate client tampering |
| SQLite/PostgreSQL behavior mismatch | Medium | PostgreSQL CI integration suite for persistence/timezone paths |
| Notification failure after check-in | Medium | Transactional outbox, retry and monitoring |
| Scope expansion | High | Feature intake gate, phased roadmap, non-goals |

## 20. ADR governance

Create one ADR for each material architecture decision. ADRs are immutable
historical records: supersede rather than rewrite accepted decisions. At
minimum, create ADRs for:
- Modular monolith and module boundaries.
- Authentication/session strategy (browser + Android).
- SQLite/PostgreSQL strategy.
- Check-in uniqueness and transaction model.
- Timezone and recurring-schedule model.
- Consent-based mentor access model.
- RBAC storage and enforcement.
- Plan-limit enforcement strategy.
- Mobile tech stack (Android).
- Outbox/background-worker strategy.
- Payment/subscription integration (when approved).

## 21. Open decisions

The following product decisions must be resolved in relevant feature SPECs
before implementation:
- Which routine types are supported initially (simple daily, weekly, monthly,
  custom RRULE-like)?
- Can a routine have multiple schedules (e.g., "3x per week on any days")?
- Are skipped check-ins (reason) recorded separately from missing check-ins?
- Should streaks be based on "done" only, or allow "skipped-but-approved" days?
- Is mentor access global (see everything) or per-routine/per-feature? Default
  should be per-feature to minimize exposure.
- Which languages/locales and currencies are supported at launch?
- Free-tier limits: max active routines? mentor feature access?
- Is mentor messaging real-time (WebSocket) or polled initially?
- Are provider/mentor subscriptions or platform commissions part of the business
  model?
- Expected user count, active routines per user, reminder volume, availability
  target, RPO, RTO?
