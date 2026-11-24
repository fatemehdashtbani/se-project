# Implementation Plan — F-032 UI/UX corrections

- Status: Implemented
- Feature spec: `docs/features/F-032-ui-ux-fixes/SPEC.md`

## Ordered steps

1. **Theme plumbing (RED first).** Add `src/shared/__tests__/theme.spec.ts` and
   `src/components/__tests__/ThemeToggle.spec.ts` for default dark, persistence,
   toggling, accessible label, and top-left positioning.
2. **Palette variables.** Map the Tailwind `slate` scale to
   `--c-slate-*` custom properties and define the dark (`:root`) and light
   (`[data-theme='light']`) values plus the non-slate foreground overrides.
3. **Theme module and control.** `shared/theme.ts` (`applyTheme`, `initTheme`,
   `useTheme`), `components/ThemeToggle.vue`, `initTheme()` in `main.ts`,
   `<ThemeToggle />` in `App.vue`, `data-theme="dark"` on `<html>` to avoid a
   flash of light content.
4. **Profile layout.** Widen the card to `max-w-2xl`/`lg:max-w-3xl` and wrap the
   profile and password fields in `grid gap-4 sm:grid-cols-2` (mobile keeps one
   field per row). New assertion in `ProfilePage.spec.ts`.
5. **Dashboard greeting.** Drop the «به‌زودی» clause and update the greeting
   assertion in `DashboardPage.spec.ts`.
6. **Forgot-password copy.** Rename the submit button and replace the success
   message with the honest "delivery not active" text; update
   `ForgotPasswordPage.spec.ts`.

## Tests

| Layer | File | Covers |
|---|---|---|
| Unit | `src/shared/__tests__/theme.spec.ts` | default theme, storage restore, toggle persistence |
| Component | `src/components/__tests__/ThemeToggle.spec.ts` | icon/label/position, click switches theme |
| Component | `src/views/__tests__/ProfilePage.spec.ts` | wide two-column grid, card width, existing flows |
| Component | `src/views/__tests__/DashboardPage.spec.ts` | greeting without the stale sentence |
| Component | `src/views/__tests__/ForgotPasswordPage.spec.ts` | no false "link sent" claim |

## Migration / rollback

No database or API contract change, so no migration. Reverting is limited to the
touched frontend files; the `slate` palette mapping is behaviour-preserving in the
dark theme, so partial rollback is safe.

## Documentation

- This folder's `SPEC.md` and `PLAN.md`.
- `Task-List.md`: new F-032 row, Done, plus a change-log entry.

## Completion checks

- `npm run type-check`
- `npm run lint`
- `npm run test:unit`
- `npm run build`

## Deliberately not done

- Real password-reset email delivery (F-022; needs an email provider and a
  single-use token table).
