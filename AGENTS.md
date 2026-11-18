# AGENTS.md — Engineering Rules for AI Agents

## 1. Mission and product context

You are contributing to a production-minded online **routine-management platform** for individuals and mentors. The system has three primary user roles:

1. **User (regular)** — creates and tracks daily/weekly/monthly routines and habits; checks in; manages subscription; grants or revokes mentor access.
2. **Mentor** — is discovered and selected by users; views a user's routines and progress **only with that user's explicit, revocable consent**; leaves comments and sends messages.
3. **Platform Administrator** — manages users, subscription plans, platform-wide configuration, and auditability; accesses the web-only admin panel.

The product is a behavioral-habit and routine-tracking platform, not merely a to-do list. Correctness of **time and time zone** (daily boundaries, weekly patterns, streaks, reminders), authorization, **consent-based privacy**, **plan-limit enforcement**, and auditability are critical.

Your job is to make the smallest correct, maintainable, secure change that satisfies an approved specification. Do not silently expand scope.

## 2. Source-of-truth hierarchy

When instructions conflict, use this order:

1. Explicit user instruction for the current task.
2. Approved feature `SPEC.md`.
3. Approved feature `PLAN.md`.
4. Accepted ADRs in `docs/adr/`.
5. `docs/SRS.md` and `docs/ARCHITECTURE.md`.
6. Existing implementation and tests.
7. Your assumptions.

Never treat an assumption as an approved requirement. Record unresolved product or technical questions in the feature spec and ask for clarification when the answer changes data integrity, security, user-visible behavior, or scope.

## 3. Mandatory feature intake gate

Before implementing any new feature or material behavior change:

1. Read this file and the relevant architecture, SRS, ADRs, and existing code.
2. Add the feature to `Task-List.md` with a unique ID (`F-###`), owner/status, dependencies, priority, and links to its documents.
3. Create a feature folder: `docs/features/F-###-short-name/`.
4. Create both `SPEC.md` and `PLAN.md` in that folder.
5. In `SPEC.md`, define problem, actors, scope, non-goals, user journey, requirements, business rules, API/UI behavior, data impact, security/privacy, edge cases, and measurable acceptance criteria.
6. In `PLAN.md`, list ordered implementation steps, tests to write first, migration/rollback approach, documentation changes, and completion checks.
7. Identify architectural decisions. If a decision changes system boundaries, data model strategy, consistency, security, deployment, integrations, or a long-lived dependency, create an ADR under `docs/adr/`. If no ADR is needed, state why in the plan.
8. Obtain human approval of the specification and plan when the work changes product behavior, data contracts, security, or architecture.
9. Only then begin implementation.

Do not create empty placeholder specs merely to bypass this gate. A small bug fix may use a lightweight issue entry, but any behavior change or feature still requires an explicit test and documented expected behavior.

## 4. Required development method: TDD

Use Red → Green → Refactor for every behavior change:

1. **Red:** Write a focused test that expresses the required behavior and fails for the expected reason.
2. **Green:** Implement the minimum code needed to pass the test.
3. **Refactor:** Improve structure without changing behavior; keep the tests green.
4. Add regression tests for discovered defects.
5. Run the relevant test suite after each meaningful change.

Do not write implementation first and retroactively add superficial tests. Tests must assert observable behavior, not private implementation details.

### Test layers

- Unit tests: pure business rules, validation, schedule evaluation, streak computation, plan-limit evaluation, time-zone math.
- Integration tests: database repositories, transactions, API endpoints, migrations, external adapter contracts.
- Contract tests: API schemas and integration payloads.
- End-to-end tests: critical journeys across browser and API (sign-up → create routine → check-in → dashboard; mentor consent grant → mentor view → comment).
- Security tests: authorization boundaries, object-level access, consent enforcement, plan-limit bypass attempts, input validation, rate limits, and session/token behavior.
- Time-zone tests: DST transitions, user time-zone change mid-streak, weekly routines across DST, reminder firing across DST.

SQLite is useful for fast local tests, but it is not a substitute for PostgreSQL integration tests. Do not claim production-grade time-zone or concurrency correctness based only on SQLite test results.

## 5. Architecture principles

- Start with a **modular monolith** and explicit domain boundaries (Identity, Routine, Check-in, Mentor, Subscription, Admin).
- Keep business rules out of FastAPI route handlers and Vue components.
- Separate API, application/use-case, domain, and infrastructure concerns.
- Depend on interfaces/ports in application logic; isolate database, email, push-notification, and payment vendors behind adapters.
- Use dependency injection at module boundaries.
- Prefer boring, proven technology over novelty.
- Avoid premature microservices, event sourcing, CQRS, distributed locks, and unnecessary abstractions.
- Make important side effects explicit and observable (e.g., audit log for consent changes).
- Use UTC for persisted instants; preserve IANA timezone identifiers for users and for interpreting routine schedules and daily boundaries.
- Never assume a local wall-clock date uniquely identifies a day across time zones.
- A user's "local day" for a check-in is determined by their **stored IANA time zone at the time of check-in**, not by the server's time zone.

## 6. Backend rules

- Use Python type hints throughout production code.
- Use FastAPI routers only for HTTP concerns: parsing, authentication context, response mapping, and status codes.
- Put use cases in application services and invariants in domain logic.
- Use Pydantic request/response schemas; never expose ORM objects directly.
- Use SQLAlchemy 2.x typed mappings and explicit transaction boundaries.
- Use Alembic for every schema change. Never rely on `create_all()` in production.
- Keep database sessions request-scoped and close them reliably.
- Do not perform network calls while holding a database transaction or row lock.
- Use stable error codes and a consistent error response envelope.
- Validate ownership, role, and **consent** server-side on every protected operation.
- Use pagination for potentially unbounded collections.
- Use idempotency keys for check-in creation and other retry-sensitive commands.
- Do not log passwords, access tokens, private routine notes, mentor messages, or unnecessary personal data.

## 7. Routine and time correctness rules

Routine and time correctness is a critical invariant:

- A user must have at most one active check-in per routine per **local calendar day**. The "day" is defined in the user's current IANA time zone at check-in time. Store each check-in with: the UTC instant, the user's IANA time zone at the time of check-in, and a denormalized `local_date` (`YYYY-MM-DD`) for uniqueness.
- Check-in uniqueness is enforced by a **database unique constraint** on `(routine_id, local_date)`. Never rely on frontend checks or application-only validation.
- Weekly/monthly routines are scheduled by **day-of-week and/or day-of-month in the user's IANA time zone**. Never assume UTC Monday is local Monday.
- Streaks (consecutive completed days) are computed in the user's time zone. DST transitions must not break a streak: a 23-hour or 25-hour day still counts as one local day.
- When a user changes their time zone, existing check-ins **retain their original local date and time zone**. New check-ins use the new time zone. Streak computation uses each check-in's stored `local_date`.
- Reminders fire at the **user's local time** for the configured routine. Reminder scheduling must explicitly handle DST gaps and repeated local times; never silently guess.
- Routine start and end dates are stored as **local dates in the user's time zone**, not UTC instants.
- A routine must retain a snapshot of material terms at check-in time (routine name, target frequency, plan tier at the time) so later edits do not rewrite historical completion-rate computation.
- Handle duplicate client retries with idempotency keys on check-in creation.
- Never rely on the frontend to determine the user's local day; use the **stored** user time zone (updatable via a dedicated endpoint).

## 8. Frontend rules

- Use Vue 3 Composition API with TypeScript and `<script setup>`.
- Keep pages, reusable components, composables, API clients, stores, and domain-specific view models separate.
- Use Pinia for shared client state only where needed; do not mirror all server state globally.
- Use a typed API client generated from or checked against the OpenAPI schema.
- Centralize authentication handling, error mapping, and request correlation.
- Validate forms for usability, but treat backend validation as authoritative.
- Provide loading, empty, success, error, and retry states.
- Ensure keyboard navigation, semantic HTML, visible focus, labels, and accessible error messages.
- Do not put authorization decisions only in the UI. Mentor-viewing-user-data must be re-checked server-side on every request.
- Avoid giant components and duplicated business logic.

## 9. API and compatibility

- Prefix public APIs with `/api/v1`.
- Use explicit request and response schemas.
- Use consistent naming, status codes, pagination, filtering, and error structures.
- Do not make breaking API changes without a documented migration/deprecation plan.
- Keep OpenAPI accurate and review generated schema changes.
- Use UTC ISO 8601 timestamps in API payloads; include the IANA time-zone identifier where local-day interpretation is required.
- Expose a dedicated `PUT /api/v1/me/timezone` for changing the user's time zone.

## 10. Security and privacy baseline

- Apply least privilege and deny by default.
- Enforce **RBAC** (`User`, `Mentor`, `Admin`) and **resource ownership** in backend use cases.
- Enforce **consent-based mentor access**: a mentor can only read a user's routines, check-ins, and progress when an **active, non-revoked** consent record exists. Revoking consent blocks access on the very next request.
- Enforce **plan limits server-side**: free-tier limits (e.g., active routine count, mentor access availability) are validated in the application service, never trusted from the client.
- **Admin endpoints** must be gated by `admin` role and produce an **audit entry** for every mutation.
- Hash passwords using a modern password-hashing algorithm such as Argon2id via a maintained library.
- Use secure, HttpOnly, SameSite cookies for browser sessions where feasible; if using bearer tokens, define refresh, revocation, storage, and CSRF/XSS mitigations in an ADR.
- Protect state-changing cookie-authenticated requests against CSRF.
- Rate-limit login, password reset, public endpoints, and check-in creation.
- Verify email addresses before enabling sensitive account actions.
- Use short-lived, single-use password-reset tokens.
- Validate uploads by type, size, and content; store outside the web root.
- Keep secrets out of source control and frontend bundles.
- Maintain **audit records for privileged actions**: role changes, consent grants/revocations, plan changes, and admin actions.
- Define retention, export, and deletion processes for personal data.
- Do not claim legal compliance (GDPR or otherwise) without a documented legal and operational review.

## 11. Database and migrations

- SQLite is the default local development database and may be used for fast unit/integration tests that do not depend on PostgreSQL-specific behavior.
- PostgreSQL is the production database and the authoritative database for concurrency, locking, JSON behavior, and production migration validation.
- Use SQLAlchemy 2.x and Alembic.
- Keep migrations deterministic, reviewed, and reversible where practical.
- Test migrations from the previous released schema against PostgreSQL.
- Avoid SQLite-specific SQL in application logic.
- Use portable types and constraints where possible; isolate PostgreSQL-specific features behind migrations/repositories and document them.
- The check-in unique constraint `(routine_id, local_date)` is portable and must be enforced in both SQLite and PostgreSQL.
- Never use SQLite in production.

## 12. External integrations and side effects

- Email, push notification (Android via FCM), and payment providers must be behind adapter interfaces.
- Use an outbox pattern for reliable delivery of notifications and reminders when required.
- Do not send an email, push notification, or call a payment API before the database transaction commits.
- Make webhook handlers (e.g., payment provider) authenticated, idempotent, and replay-safe.
- Store external event IDs and synchronization status.
- Retry transient failures with bounded exponential backoff; route exhausted failures to a reviewable failure state.
- For MVP (no Redis), use `FastAPI BackgroundTasks` for notification dispatch. When scale demands a durable queue, introduce one behind an approved ADR.

## 13. Observability and operations

- Use structured logs with request/correlation IDs and (where known) `user_id` and `role`.
- Expose health and readiness endpoints without leaking internals.
- Record metrics for API latency, error rates, check-in conflicts, reminder failures, and integration failures.
- Maintain a **separate audit log** for role changes, consent grants/revocations, plan changes, and admin actions.
- Use traces where the deployment complexity justifies them.
- Provide database backups, restore tests, migration procedures, and an incident runbook before production launch.
- Define retention and redaction for logs.
- Do not add monitoring infrastructure without a concrete operational requirement.

## 14. Code quality

- Follow the repository's formatter, linter, and type-checker configuration.
- Prefer clear names and small functions with one responsibility.
- Avoid broad exception catches; translate known exceptions at boundaries.
- Never suppress a failing test or weaken an assertion just to obtain a green build.
- Do not add dependencies without explaining why, checking maintenance/security posture, and updating the relevant ADR when material.
- Remove dead code and unused dependencies introduced by your change.
- Do not add TODO comments as a substitute for completing required work. If deferred, create a tracked task.

## 15. Required workflow for every task

Before editing:
- Inspect repository structure, relevant modules, tests, and docs.
- Read linked SPEC, PLAN, and ADRs.
- Confirm the task is approved and not blocked.
- State assumptions and likely files to change in your work plan.

During work:
- Follow TDD.
- Keep changes scoped.
- Update tests, API schemas, migrations, docs, and examples together.
- Never fabricate command output or claim tests ran if they did not.

Before completion:
- Run formatter and linter.
- Run type checks.
- Run focused tests, then the relevant full suite.
- Run PostgreSQL integration/time-zone tests when the feature touches persistence, scheduling, or check-ins.
- Review migration upgrade and rollback behavior.
- Check authorization, consent, and privacy implications.
- Update `Task-List.md`, feature `PLAN.md`, and relevant docs.
- Report exactly what changed, commands actually run, results, known limitations, and follow-up tasks.

## 16. Definition of Ready (DoR)

A feature is Ready only when:
- It has a Task-List entry and unique `F-###` ID.
- `SPEC.md` and `PLAN.md` exist and are reviewed.
- User journey and acceptance criteria are testable.
- Dependencies and non-goals are explicit.
- Data/API/security/consent/plan-limit implications are identified.
- Required ADRs exist or the plan records why none is required.
- Test strategy is defined, including PostgreSQL and time-zone tests when relevant.

## 17. Definition of Done (DoD)

A feature is Done only when:
- All acceptance criteria pass.
- TDD evidence exists in the test suite.
- Relevant unit, integration, and E2E tests pass.
- PostgreSQL-specific and time-zone tests pass where applicable.
- Authorization, consent, plan-limit, validation, error, and edge cases are covered.
- Migrations and rollback notes are complete.
- API documentation and user-facing behavior are updated.
- Logs/metrics/audit entries are adequate for operations.
- No known critical security or data-integrity defect remains.
- `Task-List.md` and `PLAN.md` are updated.
- The agent provides an honest completion report.

## 18. Agent communication protocol

For each task, report:
1. Task ID and linked specification.
2. Understanding of expected behavior.
3. Assumptions and unresolved questions.
4. Planned files/modules and tests.
5. Implementation summary.
6. Tests and commands actually executed with results.
7. Migration/operational impact.
8. Remaining risks or follow-up tasks.

If asked to implement a feature without its SPEC/PLAN, stop at the intake gate and create or request approval for those documents. Do not bypass this rule because the requested change appears small.
