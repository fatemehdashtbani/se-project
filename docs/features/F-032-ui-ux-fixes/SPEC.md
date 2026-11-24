# Feature Specification — F-032 UI/UX corrections (theme, profile layout, dashboard greeting, reset notice)

- Status: Implemented
- Owner: Project team
- Related backlog item: F-032
- Related ADRs: none — presentation-only change, no architecture or data decision

## 1. Problem and objective

Four user-visible defects were reported:

1. `/forgot-password` claimed «لینک بازیابی ارسال شد» although no email is sent
   (the backend endpoint is still the F-022 mock).
2. `/profile` was constrained to `max-w-md`, so on desktop it looked like a phone
   layout and every field occupied its own row.
3. The dashboard greeting still said «روتین‌های شما به‌زودی اینجا نمایش داده
   می‌شوند» while the routine list was already rendered below it.
4. The application only offered a dark palette; there was no way to switch to a
   light (روشن) theme, and no theme control.

## 2. Actors

- Any visitor: the theme control renders on every page (public and
  authenticated).

## 3. Scope

### In scope

- **Honest reset message.** The page keeps the request flow, but the confirmation
  no longer claims an email was delivered. The submit button is renamed to
  «درخواست بازیابی رمز» and the confirmation explains that email delivery is not
  active yet and points at the profile page for changing the password.
- **Profile layout.** The card grows to `max-w-2xl` (and `max-w-3xl` at `lg`).
  The profile fields (نام، نام خانوادگی، شماره تلفن، ایمیل) and the password
  fields are laid out in a two-column grid at `sm` and wider, and collapse back
  to one field per row below `sm` (mobile).
- **Dashboard greeting.** Only the welcome sentence remains; the outdated
  «به‌زودی نمایش داده می‌شوند» clause is removed.
- **Light/dark theme.** A fixed, top-left control with the requested
  `mdi-theme-light-dark` icon toggles between the dark (default) and light
  palettes on every route. The choice persists in `localStorage` and is applied
  before the first render.

### Non-goals

- Real password-reset email delivery (token table, mailer adapter, rate limits) —
  still F-022 and blocked on an email provider.
- Following the OS `prefers-color-scheme`, per-route themes, or additional
  palettes.
- Reworking the auth/admin layouts beyond what the palette variables provide.

## 4. Requirements

- FR-1: `/forgot-password` must never state that a reset link was sent while
  delivery is disabled.
- FR-2: On viewports `>= 640px` the profile card is wider than `max-w-md` and
  shows two fields per row; below `640px` each field occupies its own row.
- FR-3: The dashboard greeting contains the user's name and the welcome sentence
  only.
- FR-4: A control at the top-left of the viewport toggles dark ↔ light, exposes an
  accessible Persian label, and survives a reload.
- FR-5: The dark palette must look exactly as before this change.

## 5. Implementation notes

- The Tailwind `slate` scale is mapped to CSS custom properties in
  `frontend/tailwind.config.js`; `frontend/src/assets/styles/main.css` holds the
  dark values on `:root` and the light values on `[data-theme='light']`. Existing
  components keep their `bg-slate-*` / `text-slate-*` classes and both themes are
  driven by one attribute on `<html>`.
- Non-slate foreground colours that must stay legible on light surfaces
  (`text-white`, `text-blue-200/300/400`, `text-red/rose/emerald-200`) are
  overridden in the same stylesheet, with blue buttons keeping white text.
- `frontend/src/shared/theme.ts` owns the state, persistence, and
  `initTheme()` bootstrap; `frontend/src/components/ThemeToggle.vue` is rendered
  once in `App.vue`.

## 6. Acceptance criteria

- Forgot-password confirmation text contains no «لینک بازیابی ارسال شد».
- `#profile-form` and `#password-form` use a `sm:grid-cols-2` grid; the card is
  `max-w-2xl`.
- Dashboard text no longer contains «به‌زودی».
- Clicking the top-left control sets `document.documentElement.dataset.theme` to
  `light` (and back), and the value is persisted.
- `npm run type-check`, `npm run lint`, `npm run test:unit`, and `npm run build`
  pass.
