# ADR-0012: Android Client Tech Stack

- **Status:** Proposed — must be decided before F-015 (android-app) starts
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The platform needs an Android client for end users: routine viewing, check-in,
and push notifications (FCM). The client consumes the same `/api/v1` REST API
as the web frontend. The tech stack is not yet decided.

## Candidates

1. **Flutter (Dart)**
   - Pros: strong cross-platform (iOS later), mature ecosystem, good
     performance, single codebase.
   - Cons: new language (Dart) for the team; separate from Vue/TypeScript
     skill set.

2. **React Native (JavaScript/TypeScript)**
   - Pros: TypeScript shares mental model with the Vue frontend; large
     ecosystem; FCM support mature.
   - Cons: introduces React (a second framework) into the project; heavier
     setup than Flutter; occasional native module issues.

3. **Kotlin (native Android)**
   - Pros: best performance and platform integration; mature tooling.
   - Cons: Android-only (iOS would need a separate build later); steepest
     learning curve for a web-focused team.

## Decision

**Deferred.** A separate ADR (this one, finalized) will be accepted before
F-015 starts. The selected stack must:

- Consume the same `/api/v1` API (no special endpoints for mobile).
- Respect RBAC, ownership, consent, and plan-limit checks — no client-side
  bypass.
- Support push notifications via FCM.
- Store tokens in secure storage (Android Keystore).
- Target Android 8.0+ (API 26+).

## Decision criteria (to be used when finalizing)

1. Team familiarity and learning cost.
2. Reuse of TypeScript skills from the Vue frontend.
3. Long-term maintenance and hiring.
4. Performance needs for routine/check-in UX (moderate).
5. Need for iOS in the medium term.

## Alternatives considered

All three candidates above are viable; the decision is pending.

## Consequences

- Until this ADR is accepted, F-015 is **Blocked**.
- The API contract (`/api/v1`) is stack-agnostic and does not change based on
  this decision.
- The web app continues independently of this decision.

## References

- Task-List.md (F-015)
- AGENTS.md §3 (tech baseline)
- ADR-0005 (JWT strategy) — Android uses bearer flow
- ADR-0010 (no Docker)
