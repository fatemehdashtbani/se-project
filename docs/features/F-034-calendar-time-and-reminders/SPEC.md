# F-034 — Calendar event time and same-day reminders

## Purpose

Events currently carry a day only. Users who want to do something at a specific
hour cannot record it, and nothing reminds them on the event day. This feature
adds an optional time to a calendar event and notifies the user about the
events of the current day.

## Scope

In scope: an optional `event_time` on `calendar_events`, accepting and returning
it through the existing endpoints, a time input on `/calendar` (displayed in
Persian digits), and a same-day reminder banner in the app plus an optional
browser notification.

Out of scope: recurring events, push notifications on mobile, email reminders,
time zones on events (the time is a plain local wall-clock time), and editing an
existing event.

## User journeys

1. The user selects a day, types a title, optionally picks a time such as
   `14:30`, and adds the event. The event list shows the Jalali date and the
   Persian time.
2. On the day of an event the user sees a «رویدادهای امروز» banner on every
   signed-in page, above the bottom navigation, listing today's events and their
   times.
3. If the user allows browser notifications, the app sends one notification for
   today's events when it loads and one notification at the event's time.

## Functional requirements

- **FR-F034-001** — `event_time` is optional (`HH:MM`, 24-hour local time). An
  event without a time still works exactly as before.
- **FR-F034-002** — The create payload and every event response include
  `event_time` (`"14:30:00"` or `null`). The value is validated by Pydantic as
  an ISO time; invalid input answers `422 VALIDATION_ERROR`.
- **FR-F034-003** — Ownership and window filtering are unchanged; `event_time`
  is never used to widen or bypass the owner filter.
- **FR-F034-004** — Today's events are events whose `event_date` equals the
  client's local day. The banner is dismissible per day and remembers the
  dismissal in `localStorage`.
- **FR-F034-005** — Browser notifications are opt-in. The banner offers an
  «فعال کردن اعلان مرورگر» button while permission is `default`; without
  permission the in-app banner is the only reminder.
- **FR-F034-006** — The summary browser notification is sent at most once per
  day for the same set of event ids; a timed event also notifies at its time,
  including when that time passes while the app stays open.

## Data model

| Table | Change |
|---|---|
| `calendar_events` | `event_time` (`time`, nullable) added after `event_date` |

Migration `d5a2f8c1e6b4` adds the column; downgrade drops it.

## API

| Method | Path | Change |
|---|---|---|
| POST | `/api/v1/calendar-events` | accepts optional `event_time` |
| GET | `/api/v1/calendar-events?start=&end=` | items carry `event_time` |

## UI

- `/calendar` — add form gains «ساعت (اختیاری)»; the month list shows the time
  under the Jalali date in Persian digits.
- Every signed-in page — `TodayReminders` banner above `BottomNav` with today's
  events, times, a browser-notification opt-in and a dismiss control.

## Edge cases

- An event at `23:59` on the current day still notifies that day.
- Events without a time are listed first in the banner and never schedule a
  timed notification.
- A dismissed banner stays dismissed for the rest of that day only.
- An unsupported `Notification` API degrades to the in-app banner.
- Deleting an event removes it from the banner through the shared store.

## Security and privacy

- The banner reads only the signed-in user's events from the existing
  owner-scoped endpoint.
- Notification text contains the event title the user wrote; no account data.
- No new secrets, endpoints, dependencies, or third parties.

## Acceptance criteria

- Backend tests cover creating with and without a time and returning
  `event_time` in list responses.
- Store tests cover posting `event_time`; calendar helper tests cover the
  Persian time label.
- `ruff`, `mypy`, `pytest`, `type-check`, `lint`, `vitest`, and `build` pass.
- Migration `d5a2f8c1e6b4` upgrades and downgrades cleanly.
