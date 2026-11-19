# Implementation Plan — F-023 Frontend Auth Integration

- Status: Approved
- Related SPEC: `SPEC.md`

## 1. Implementation approach
1. Setup a typed API client (fetch or axios) in `frontend/src/shared/api/client.ts`.
2. Create the Pinia store in `frontend/src/stores/auth.ts`.
3. Update `LoginPage.vue` to use the store.
4. Create a placeholder `DashboardPage.vue` and router guard.

## 2. Ordered tasks
1. Create the API client and Pinia store (TDD: test the store first).
2. Update `LoginPage.vue` to call the store on submit. Update tests to mock the store.
3. Create `DashboardPage.vue` and add the `/dashboard` route with `meta: { requiresAuth: true }`.
4. Implement the router guard using the Pinia store.

## 3. Completion checklist
- [ ] Pinia store tested.
- [ ] Login actually hits the backend.
- [ ] Router guards work.
- [ ] Linters pass.
