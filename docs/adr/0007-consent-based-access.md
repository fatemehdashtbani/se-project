# ADR-0007: Consent-Based Mentor Access Model

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

A mentor may only view a user's routines, check-ins, and progress when that
user has explicitly and revocably granted access. Consent must be scoped
(minimal exposure by default), immediately revocable, and fully auditable.
Accessing another user's data without consent is a privacy violation and a
security-relevant event.

## Decision

**Entity: `mentor_grant`**
- Columns: `id`, `user_id` (FK), `mentor_id` (FK to users with role=mentor),
  `scope` (JSON or enum list), `granted_at`, `revoked_at` (NULL = active),
  `created_at`, `updated_at`.
- A grant is **active** when `revoked_at IS NULL`.
- At most one active grant per (user_id, mentor_id).
- Unique partial index (PostgreSQL) / equivalent application check
  (SQLite) to enforce this.

**Scope model (minimal by default):**
- Per-routine sharing is the default: the user selects which routines to
  share.
- Optional feature flags per grant: `allow_comments`, `allow_messages`.
- Global "see everything" is **not** supported.

**Enforcement:**
- Every mentor read request for a user's routine/check-in data checks
  `mentor_grant` for an active record with the requested routine in scope.
- Revocation sets `revoked_at`; the mentor's very next request is denied.
- All grant/revoke events are written to the audit log with actor, target,
  scope, and timestamp.
- Access attempts without an active grant return HTTP 403 and are logged as
  security-relevant events.

**User control:**
- A dedicated endpoint allows users to list, grant, and revoke mentor grants.
- Revocation is idempotent and immediate.

## Alternatives considered

- **Global consent (mentor sees everything).** Rejected: violates data
  minimization; increases blast radius of a compromised mentor account.
- **Consent with no scope (all-or-nothing).** Rejected: forces users to
  over-share. Per-routine scope is minimally invasive.
- **Time-limited consent (auto-expire).** Considered; deferred. Users can
  revoke manually; auto-expiry can be added later without schema change.

## Consequences

- Consent enforcement is mandatory on every mentor-facing read.
- Tests must cover: no grant → 403; active grant → 200; revoke → immediate
  403; scope violation → 403; audit log entry for grant/revoke.
- Mentor UI shows the scope explicitly; users see the scope when granting.
- The audit log is the authoritative record for disputes.

## References

- AGENTS.md §10, §12
- ARCHITECTURE.md §6, §7, §13
- ADR-0006 (RBAC model)
- F-011 (mentor access feature)
