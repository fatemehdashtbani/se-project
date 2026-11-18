# ADR-0006: Role-Based Access Control (RBAC) Model and Storage

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The platform has three roles: User, Mentor, Admin. Authorization is not
sufficient with a role check alone; ownership and consent must also be
enforced on every protected operation. Roles must be assignable only through
controlled paths (no self-assignment of `mentor` or `admin`).

## Decision

**Role storage:**
- A single `role` column on the `users` table with values `user`, `mentor`,
  `admin`.
- A user starts as `user` after registration.
- `mentor` is granted by Admin after a verification workflow.
- `mentor` users **retain user capabilities** (can create own routines).
- `admin` is a separate role; created only via secure seeding or explicit
  DB-level promotion (never through public UI).
- Sub-roles for admin (e.g., support, moderator, finance) are deferred to a
  future ADR.

**Enforcement:**
- RBAC checks live in the **application/use-case layer**, not only in route
  guards or UI.
- Every protected operation performs, in order:
  1. Authentication (valid token).
  2. Role check (required role present).
  3. Ownership check (resource belongs to the caller or caller is admin).
  4. Consent check (for mentor accessing user data).
  5. Plan-limit check (for plan-gated operations).
- Failures return HTTP 403 with a stable error code, and security-relevant
  denials are logged.
- Admin mutations are audited (see ARCHITECTURE.md §13).

## Alternatives considered

- **Separate `roles` and `permissions` tables with many-to-many.** Rejected:
  over-engineering for three fixed roles; deferred until custom admin
  sub-roles are introduced.
- **JWT claims alone for role.** Rejected: roles change server-side; stale
  tokens must not grant access after a role is revoked. Roles are re-checked
  from the DB on protected operations.

## Consequences

- Role changes take effect immediately (no waiting for token expiry).
- Role checks are centralized in application services, not scattered.
- Admin sub-roles require a future ADR that extends this model.
- Tests must cover: user cannot self-assign `mentor`/`admin`; mentor cannot
  act as admin; admin mutations audited.

## References

- AGENTS.md §10
- ARCHITECTURE.md §7
- ADR-0005 (JWT strategy)
- ADR-0007 (consent-based access)
