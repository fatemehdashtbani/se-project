# ADR-0003: Check-in Uniqueness per Local Day

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

A user may attempt to check in the same routine multiple times on the same
local day — due to double-clicks, network retries, or multiple devices.
Without database-level enforcement, duplicate check-ins corrupt streak counts
and completion-rate calculations.

This ADR adapts the booking-overlap concern of the scheduling platform (where
intervals can overlap arbitrarily and require PostgreSQL exclusion constraints
over tstzrange) to the simpler routine-tracking invariant:

**At most one active check-in per routine per user's local calendar day.**

Unlike booking, routine check-ins have no interval semantics. Two check-ins on
the same day are unambiguously a violation; there is no legitimate partial
overlap. This makes a UNIQUE constraint sufficient and portable.

## Decision

Enforce uniqueness with a database UNIQUE constraint on
(routine_id, local_date), where local_date is a DATE column computed at
check-in time from the user's IANA timezone (stored on the user record and
snapshotted per check-in).

The application layer:
1. Resolves the user's current IANA timezone.
2. Computes local_date from the UTC check-in instant and that timezone.
3. Attempts the INSERT with the unique constraint.
4. On conflict, returns HTTP 409 with a stable error code (e.g.,
   CHECK_IN_ALREADY_EXISTS_TODAY).

The POST endpoint accepts an Idempotency-Key header so that client retries
return the original check-in rather than producing a conflict.

## Alternatives considered

- **Application-only check (SELECT then INSERT).** Rejected: unsafe under
  concurrent requests, no database-level guarantee.
- **PostgreSQL exclusion constraint over tstzrange.** Rejected: overkill for
  day-level uniqueness; requires btree_gist; not portable to SQLite, forcing
  divergent dev/prod paths.
- **Soft uniqueness via triggers.** Rejected: adds complexity without benefit
  over a native constraint.

## Consequences

- The same constraint works identically on SQLite (dev/test) and PostgreSQL
  (prod).
- No PostgreSQL-specific extension is required for this invariant.
- Users can edit an existing check-in for the same local day (status/note)
  but cannot create a second one.
- Timezone correctness is still tested against PostgreSQL in CI for other
  paths (streak computation, DST handling, reminder scheduling).
- The uniqueness check is a prerequisite for correct streak calculation and
  completion-rate computation.

## References

- ARCHITECTURE.md §8.2, §9
- ADR-0004 (timezone model)
