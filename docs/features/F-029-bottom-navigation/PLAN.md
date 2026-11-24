# Implementation Plan — F-029 Bottom Navigation

- Status: Done
- Related SPEC: `SPEC.md`

## 1. Implementation approach
1. Write RED tests for the new `LogoutIcon`, `BottomNav` links/icons/logout behavior, and page integration.
2. Create `LogoutIcon.vue` from the supplied SVG.
3. Create `BottomNav.vue` with the fixed dark-theme flex layout and RouterLinks/button.
4. Mount `BottomNav` in the dashboard and profile pages, add `pb-24`, and swap the header logout text for the icon.
5. Run the full unit suite, lint, and type-check; then commit and push.

## 2. Completion checklist
- [x] `LogoutIcon.vue` matches the supplied SVG.
- [x] `BottomNav.vue` renders on both authenticated pages.
- [x] Logout signs out and redirects to `/login`.
- [x] Unit tests, lint, and type-check pass.
