# ADR-0009: Plan-Limit Enforcement Strategy

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The platform offers Free and Paid subscription plans. Plan limits (e.g., max
active routines, mentor feature access) must be enforced server-side. Trusting
the client (UI hiding, feature flags in the frontend) is a security defect:
users can bypass client checks.

## Decision

**Model:**
- `plans` table: id, code, name, price, currency, billing_cycle,
  limits (JSONB), features (JSONB), active, created_at, updated_at.
- `subscriptions` table: id, user_id, plan_id, status (active, cancelled,
  past_due), current_period_start, current_period_end, created_at,
  updated_at.
- A user's effective plan is resolved from the active subscription (or Free
  plan if none).

**Enforcement:**
- Every plan-gated operation (create routine, access mentor features,
  etc.) checks limits in the **application service layer** before the DB
  write.
- The check reads the user's current plan and current usage (e.g., active
  routine count) inside the transaction.
- On limit exceed: return HTTP 402 or 403 with a stable error code (e.g.,
  PLAN_LIMIT_REACHED) and a Persian localizable message.
- Plan changes (upgrade/downgrade) are recorded in the audit log.
- Downgrade does **not** delete data: excess routines over the new limit
  become read-only until the user resolves them (archives or upgrades).

**Admin:**
- Admins manage plans via the admin panel.
- Deleting a plan with active subscriptions is prohibited; deactivate
  instead.
- Price changes apply only to new subscriptions; existing subscribers
  grandfathered until renewal (configurable).

## Alternatives considered

- **Client-side checks only.** Rejected: trivially bypassable.
- **Entitlement service (separate microservice).** Rejected: overkill for a
  modular monolith; adds operational complexity.
- **Hard-coded limits in code.** Rejected: requires redeploy to change
  limits; plans become configuration, not code.

## Consequences

- Usage counters (e.g., active routine count) must be maintained per user.
- Limits are inspectable via `GET /api/v1/subscriptions/me`.
- Tests must simulate client tampering (direct API calls exceeding limits)
  and verify server rejection.
- Billing integration (payment provider) is a future ADR; this ADR only
  covers enforcement, not payment collection.

## References

- AGENTS.md §10 (plan limits)
- ARCHITECTURE.md §7, §13
- F-013 (subscription plans)
- Future ADR: payment provider integration
