# Implementation Plan — [FEATURE-ID] [Feature Name]

- Status: Draft / Review / Approved / In Progress / Done
- Related SPEC: `SPEC.md`
- Related ADRs:

## 1. Implementation approach
Summarize the design and boundaries.

## 2. Ordered tasks
For each task list:
- Files/modules expected to change.
- Test to write first (Red).
- Minimum implementation (Green).
- Refactor/quality work.
- Documentation/API/migration impact.

## 3. Database and migration plan
Include constraints, indexes, migration order, backfill, rollback, and
PostgreSQL-specific behavior. Note any SQLite/PostgreSQL differences for
timezone or uniqueness constraints.

## 4. API and frontend plan
List endpoint/schema and UI changes.

## 5. Test plan
Unit, integration, contract, E2E, authorization, consent enforcement,
time-zone/DST, uniqueness/conflict, and failure-path tests as applicable.

## 6. Observability and operations
Logs, metrics, alerts, retries, and runbook updates.

## 7. Risks and mitigations

## 8. Rollout and rollback

## 9. Completion checklist
- [ ] Acceptance criteria pass.
- [ ] TDD tests added.
- [ ] Relevant SQLite tests pass.
- [ ] PostgreSQL integration/time-zone tests pass where applicable.
- [ ] Consent and plan-limit checks verified where applicable.
- [ ] Lint/type checks pass.
- [ ] Migration reviewed and tested.
- [ ] Security/privacy review complete.
- [ ] Docs and Task-List updated.
