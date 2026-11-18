# ADR-0011: Background Jobs via FastAPI BackgroundTasks (MVP)

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The platform needs asynchronous work: sending verification emails, password
reset emails, reminder emails, push notifications (Android via FCM), and
audit-related writes. Redis and a dedicated worker are excluded from MVP
(ADR-0010).

## Decision

**MVP approach:**
- Use **FastAPI BackgroundTasks** for fire-and-forget dispatch of
  non-critical work (emails, push notifications).
- Use an **outbox table** (`outbox_messages`: id, type, payload, status,
  attempts, last_error, created_at, next_attempt_at, processed_at) for work
  that must be reliably delivered.
- A lightweight in-process scheduler (e.g., APScheduler) triggers periodic
  outbox processing and reminder checks at a bounded interval (e.g., every
  60 seconds).
- Retries are bounded (e.g., max 5 attempts) with exponential backoff;
  exhausted messages are marked `failed` and surfaced in admin metrics.
- Notification failures never roll back the triggering transaction
  (check-in, consent change, etc.).

**Out of scope for MVP (deferred):**
- Durable external queue (Redis/Celery/RQ/SQS).
- At-least-once exactly-once guarantees beyond outbox.
- Real-time WebSocket delivery.

**Scale-up path:**
- When dispatch volume or reliability requirements exceed MVP capacity,
  introduce a durable queue via a new ADR (likely Redis-backed Celery or
  RQ).

## Alternatives considered

- **Celery + Redis from day one.** Rejected: violates ADR-0010; adds
  Redis + worker processes + operational overhead.
- **Pure FastAPI BackgroundTasks without outbox.** Rejected: no retry, no
  durability; lost work on crash.
- **Cron-only scheduler.** Rejected: insufficient for sub-minute reminder
  precision and no retry semantics.

## Consequences

- The outbox table is part of the schema from Phase 1.
- Reminder scheduling logic must be idempotent and deduplicated.
- DST-safe reminder scheduling is required (see ADR-0004).
- Admin metrics must include `failed` outbox count.
- Migration to a durable queue later is possible without schema change
  (outbox stays; the dispatcher changes).

## References

- AGENTS.md §12 (external integrations)
- ARCHITECTURE.md §14
- ADR-0004 (timezone)
- ADR-0010 (no Redis)
