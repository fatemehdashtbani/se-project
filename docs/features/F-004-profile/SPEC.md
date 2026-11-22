# Feature Specification — F-004 Profile and Timezone UI

- Status: Implemented
- Owner: Project team
- Related backlog item: F-004
- Related ADRs: ADR-0004 (Timezone), ADR-0008 (FarsiUI)

## 1. Problem and objective
Users need a page to view their account details and update their timezone. The timezone is critical for F-005 (Routine) to correctly calculate "today".

## 2. Scope
### In scope
- A Vue view `ProfilePage.vue` accessible at `/profile`.
- Display the user's email (read-only).
- A dropdown to select the IANA timezone (e.g., Asia/Tehran, UTC, Europe/London, America/New_York).
- Connect to `PUT /api/v1/auth/me/timezone`.
- Show success and error messages in Persian.

### Out of scope
- Changing password or email (deferred to F-022).
- Avatar uploads.

## 3. Functional requirements
- FR-F004-001: The `/profile` route must require authentication.
- FR-F004-002: The page must display the user's current email.
- FR-F004-003: The timezone dropdown must be pre-selected with the user's current timezone.
- FR-F004-004: Submitting the form must call the API and update the Pinia store on success.
- FR-F004-005: If the API returns an error, display a Persian error message.

## 4. Test strategy
- Vitest: Mock the store and API. Test rendering, pre-selection, and submission.
