# Implementation Plan — F-025 Frontend Registration UI

- Status: Approved
- Related SPEC: `SPEC.md`

## 1. Implementation approach
1. Add a `register(email, password)` action to `authStore`. It will call `POST /api/v1/auth/register`, then immediately call the existing `this.login(email, password)` action to establish the session.
2. Create `RegisterPage.vue` with the form and validation logic.
3. Add the route and links.

## 2. Ordered tasks
1. **RED:** Write tests for `authStore.register()`.
2. **RED:** Write tests for `RegisterPage.vue` (validation, calling store, Persian errors).
3. **GREEN:** Implement `register` in the store.
4. **GREEN:** Implement `RegisterPage.vue`.
5. **GREEN:** Update `router/index.ts` and `LoginPage.vue` (add link).

## 3. Completion checklist
- [x] Tests pass.
- [x] Links between login and register work.
- [x] Linters pass.
