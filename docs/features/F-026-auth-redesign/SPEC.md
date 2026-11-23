# Feature Specification — F-026 Auth UI Redesign & Profile Fields

- Status: Implemented
- Owner: Project team
- Related backlog item: F-026
- Related ADRs: ADR-0008 (FarsiUI)

## 1. Problem and objective
The professor requested a specific UI design for the login page and additional user fields (First Name, Last Name, Username, Phone). We need to update the backend schema and completely redesign the auth frontend.

## 2. Scope
### In scope
- Add `username`, `first_name`, `last_name`, `phone_number` to the `User` model.
- Redesign `LoginPage.vue` and `RegisterPage.vue` with a split-screen layout (Image right, Form left), dark theme, and "Routine Code" branding.
- Connect the new fields to the backend.
