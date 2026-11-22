# Implementation Plan — F-004 Profile and Timezone UI

- Status: Approved
- Related SPEC: `SPEC.md`

## 1. Implementation approach
1. Update `authStore` to add `updateTimezone(timezone)` action.
2. Create `ProfilePage.vue`.
3. Add the route to the router with `meta: { requiresAuth: true }`.

## 2. Ordered tasks
1. **RED:** Write tests for `ProfilePage.vue` (renders email, shows timezone dropdown, calls store on submit).
2. **RED:** Write tests for `authStore.updateTimezone()`.
3. **GREEN:** Implement `updateTimezone` in the store.
4. **GREEN:** Implement `ProfilePage.vue` with a curated list of timezones.
5. **GREEN:** Add the route and a link from the Dashboard to the Profile page.

## 3. Completion checklist
- [x] Tests pass.
- [x] RTL and Persian text correct.
- [x] Route guarded.
