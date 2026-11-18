# ADR-0001: Start with a Modular Monolith

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The product is an early-stage routine-management platform. Core workflows
require strongly consistent transactions across routines, check-ins, and
consent state. The team needs rapid iteration and manageable operational
complexity.

## Decision

Build the backend as a modular monolith with explicit domain boundaries
(Identity, Routine, Check-in, Mentor, Subscription, Admin) and one primary
relational database. Do not introduce microservices in the initial releases.

## Alternatives considered

- **Microservices from day one.** Rejected: premature for an early-stage
  product; adds network boundaries, deployment complexity, and distributed
  consistency problems without proven need.
- **Single-layer application without domain modules.** Rejected: reduces
  clarity, couples domains, and makes future extraction harder.

## Consequences

- Simpler deployment, debugging, and transactional consistency.
- Clear module boundaries preserve future extraction options.
- Modules must avoid cross-domain database shortcuts and cyclic
  dependencies.
- A service extraction requires a new ADR supported by measurable scaling or
  organizational needs.

## References

- ARCHITECTURE.md §4.1
- ADR-0002 (database environments)
