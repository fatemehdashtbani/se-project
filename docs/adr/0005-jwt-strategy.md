# ADR-0005: JWT Authentication Strategy (Cookie for Web, Bearer for Android)

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The platform has two first-class clients: a browser-based Vue 3 web app and a
native Android app. A single authentication mechanism cannot serve both
optimally:

- Browsers benefit from HttpOnly, Secure, SameSite cookies that JavaScript
  cannot read (mitigating XSS token theft) with CSRF protection.
- Native Android clients cannot reliably use cookies; they need bearer tokens
  in secure storage with explicit refresh handling.

The system must support session revocation, token rotation, and cross-client
logout. It must not store long-lived credentials in web localStorage.

## Decision

Adopt a hybrid token model:

**Browser (web) clients:**
- Short-lived JWT access token (TTL 15 minutes) delivered in a Secure,
  HttpOnly, SameSite=Lax cookie scoped to the API origin.
- Long-lived refresh token (TTL 14 days) in a separate HttpOnly cookie.
- All state-changing requests include a CSRF token header validated
  server-side (double-submit cookie pattern).
- Refresh token rotation on every refresh; the previous token is invalidated.
- Logout clears both cookies and revokes the refresh token server-side.

**Android clients:**
- Access token (TTL 15 minutes) returned in the JSON response body.
- Refresh token (TTL 30 days, rotated on each use) stored in Android Keystore
  via EncryptedSharedPreferences.
- Bearer header `Authorization: Bearer <access>` on every request.
- Logout revokes the refresh token server-side.

**Shared:**
- Refresh tokens are stored hashed in the database (e.g., SHA-256 of the
  token) with user_id, client_type, issued_at, expires_at, revoked_at.
- Revocation list checked on every refresh.
- Server issues a new access token only after validating the refresh token.
- Passwords hashed with Argon2id (see AGENTS.md §10).

## Alternatives considered

- **A) Cookie-only for all clients.** Rejected: native Android cannot manage
  cookies reliably; forces awkward custom implementation.
- **B) Bearer-only (localStorage) for all clients.** Rejected: exposes web
  tokens to XSS; violates AGENTS.md §10 guidance.
- **C) Hybrid cookie + bearer (chosen).** Each client uses the mechanism
  best suited to its threat model, while sharing the same token service.

## Consequences

- Two token delivery paths must be tested independently.
- CSRF protection is mandatory for cookie-authenticated endpoints.
- Refresh token rotation is mandatory; replay detection must be implemented.
- The Android app must implement refresh-retry logic on 401.
- A single `/api/v1/auth/*` service serves both clients with a `client_type`
  hint (`web` or `android`) to select the delivery mechanism.
- Admin sessions are separate (see ADR-0006 / future admin MFA ADR).

## References

- AGENTS.md §10 (security baseline)
- ARCHITECTURE.md §7, §16
- ADR-0006 (RBAC model)
