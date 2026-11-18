# ADR-0002: SQLite for Local Development, PostgreSQL for Production

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

Fast local setup is desirable, while production needs robust transactional
behavior and database-level guarantees for check-in uniqueness and time-zone
correctness. Docker and containerized local stacks are out of scope for this
project (see ADR-0010).

## Decision

Use SQLAlchemy 2.x and Alembic. SQLite is the default local development
database and may be used for fast portable tests. PostgreSQL is mandatory in
production and for authoritative integration, migration, and time-zone
correctness tests.

## Alternatives considered

- **PostgreSQL everywhere (including local).** Rejected: slower local
  iteration, additional setup burden; conflicts with the no-Docker constraint.
- **SQLite everywhere (including production).** Rejected: insufficient
  concurrency, no server-side enforcement, not suitable for production
  workloads.

## Consequences

- Application logic should remain portable where practical.
- PostgreSQL-specific constraints and SQL must be isolated and documented.
- CI must run a PostgreSQL test job for time-zone and persistence
  correctness.
- SQLite results alone cannot establish time-zone or production-grade
  correctness.

## References

- ARCHITECTURE.md §11
- ADR-0003 (check-in uniqueness)
- ADR-0004 (timezone model)
- ADR-0010 (no Docker)
