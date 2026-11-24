# Feature Specification — F-029 Bottom Navigation

- Status: Done
- Owner: Project team
- Related backlog item: F-029

## 1. Problem and objective
Authenticated pages had no persistent navigation: visitors had to rely on header links to reach the dashboard, routines, profile, or logout. Add a fixed bottom navigation bar shared by all authenticated pages and give logout a dedicated SVG icon instead of a text-only control.

## 2. Scope
### In scope
- A shared `BottomNav.vue` component fixed to the bottom of the viewport with four evenly spaced items: خانه, روتینها, پروفایل, خروج.
- A dedicated `LogoutIcon.vue` using the supplied 24×24 `currentColor` SVG.
- Integration into `DashboardPage.vue` and `ProfilePage.vue`, the two authenticated routes, with bottom padding so content is not hidden.
- Replacing the dashboard header's text logout control with the new icon.

### Out of scope
- Navigation on public pages (login, register, forgot-password).
- Backend or API changes.

## 3. Functional requirements
- FR-F029-001: The navigation bar is visible on `/dashboard` and `/profile` and stays fixed at the bottom (`fixed bottom-0 left-0 w-full z-50`).
- FR-F029-002: Home and routines link to `/dashboard`; profile links to `/profile`.
- FR-F029-003: The logout item signs the visitor out through `authStore.logout()` and redirects to `/login`, even if the server rejects the revoke.
- FR-F029-004: The logout icon renders the supplied SVG with `fill="currentColor"`, `width="24"`, and `height="24"`.

## 4. Test strategy
- Vitest component tests for the navigation links, icons, and logout redirect.
- Page tests asserting `BottomNav` is rendered on both authenticated pages.
- `npm run lint` and `npm run type-check` must pass.
