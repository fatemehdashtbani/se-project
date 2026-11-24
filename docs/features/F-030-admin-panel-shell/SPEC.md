# Feature Specification — F-030 Admin Panel UI Shell

- Status: Done
- Owner: Project team
- Related backlog item: F-030 (UI shell precursor to F-014)
- Dependencies: F-003 (RBAC), F-023 (frontend auth), F-029 (logout icon/bottom nav)
- Related ADRs: ADR-0006 (RBAC model) — no new ADR: this reuses the existing role model and adds no new system boundary, data store, or integration.

## 1. Problem and objective
The reference project (`D:\talebi-project\auction-shop-dev.zip`) provides a useful pattern for authenticated navigation: an RTL auth shell, role-aware post-login routing, a role guard with an access-denied page, and a sidebar layout whose admin area starts as a placeholder. This repository has working Persian sign-in/sign-up pages but no admin-facing structure at all. Provide that shell so the admin area can be grown without retesting navigation each time.

## 2. Scope
### In scope
- `panelPath(role)` + Persian `roleLabels`: admins land on `/admin`, everyone else on `/dashboard`.
- Reference-style headings on the existing Persian login and registration pages.
- `/admin` route with `requiresAuth` + admin-role guard, an RTL dark `AdminLayout` with `AdminSidebar`, an admin landing page, and two clearly-labelled placeholder sections (users, plans).
- `/forbidden` page for an authenticated visitor who lacks the required role.
- Logout from the admin sidebar through the existing auth store and `LogoutIcon`.

### Out of scope
- Any admin API endpoint, user/plan mutation, audit log, or data contract change — this is F-014.
- Client-side role assignment or admin self-registration. The reference's role picker is buyer/seller only; here roles remain server-assigned (`admin` is promoted via `scripts/create_admin.py`).
- The reference's localStorage simulation, theme toggle, animations, and React components.
- Bottom navigation on admin pages (the sidebar replaces it).

## 3. User journey
1. An admin signs in through the existing Persian `/login` page and is taken to `/admin`.
2. The admin shell shows a right-hand RTL sidebar with dashboard, users, plans, back-to-app, profile, and logout items; content renders on the left.
3. A non-admin who navigates to `/admin` sees the Persian 403 page with a link back to their own panel. A guest is sent to `/login`.
4. A visitor with any role signs up through `/register` and is taken to `/dashboard` (never to `/admin`).

## 4. Functional requirements
- FR-F030-001: `panelPath('admin') === '/admin'`; `panelPath('user' | 'mentor' | null) === '/dashboard'`.
- FR-F030-002: Login and registration redirect via `panelPath(authStore.user?.role)`.
- FR-F030-003: `/admin` and its children require an authenticated session **and** `role === 'admin'`; guests go to `/login`, other roles go to `/forbidden`.
- FR-F030-004: The admin shell is RTL, dark-themed, and includes the sidebar items with Persian labels plus a logout control using `LogoutIcon`.
- FR-F030-005: Admin landing and section pages are visibly marked as under development; they do not pretend to load or change data.
- FR-F030-006: The UI guard is a navigation aid only; server-side enforcement of admin operations remains mandatory in F-014.

## 5. Security and privacy
- No role is read from a request body or stored in localStorage; the role comes from the server session via `GET /api/v1/auth/me`.
- No personal data is rendered by the shell beyond the already-displayed account name/role.
- Admin logout revokes the session through `POST /api/v1/auth/logout` and clears local state.

## 6. Test strategy
- Unit tests for `panelPath`/`roleLabels`.
- Router tests for guest, wrong-role, and admin access to `/admin` and `/forbidden`.
- Component tests for the admin shell/sidebar/landing/403 page and for role-aware redirects in the two auth pages.
- `npm run test:unit`, `npm run lint`, `npm run type-check`; dev-server smoke check.
