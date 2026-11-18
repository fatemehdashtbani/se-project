# ADR-0004: UTC Instants and IANA Timezones for Routine Tracking

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

Users define routines and check in from their own local civil time, and may
change timezone (travel, relocation). Streaks, "today's routines," and
reminders must be correct across timezone changes and daylight-saving
transitions.

## Decision

Persist check-in instants in UTC. Store the user's timezone preference as an
IANA timezone identifier (e.g., Asia/Tehran). On each check-in, also snapshot
the IANA timezone at the time of check-in, and compute local_date
(YYYY-MM-DD) from that timezone.

Interpret routine schedules (day-of-week, day-of-month) in the user's local
timezone. Convert reminder times to UTC for scheduling, using the user's
timezone at the time the reminder is scheduled.

Define explicit behavior for DST gaps and repeated local times in the
routine-scheduling feature specification (F-006). Never silently guess.

## Alternatives considered

- **Store local times as strings without timezone.** Rejected: ambiguous
  across DST and timezone changes; breaks streak and reminder correctness.
- **Store naive timestamps and rely on server timezone.** Rejected: incorrect
  for users in other timezones; produces duplicate or missing check-ins.
- **Use numeric UTC offsets only.** Rejected: an offset (e.g., +03:30) cannot
  represent DST transitions; IANA identifiers are required.

## Consequences

- Do not store naive timestamps for check-ins or reminders.
- When a user changes timezone, prior check-ins retain their original
  local_date and timezone; new check-ins use the new timezone. Streak
  computation walks stored local_date values.
- Use a maintained timezone-aware library (e.g., Python zoneinfo, JS Intl /
  Temporal).
- Test DST gaps, repeated times, and cross-timezone display in F-006 and
  F-007.
- API contracts must distinguish UTC instants from local local_date values.

## References

- ARCHITECTURE.md §8
- ADR-0003 (check-in uniqueness)
- F-006 (routine scheduling)
- F-007 (check-in tracking)
