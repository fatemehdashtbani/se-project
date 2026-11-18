# ADR-0008: FarsiUI Integration Strategy for Vue 3

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

FarsiUI (https://farsiui.ir) is a Persian-first, RTL-native UI component
registry. Its official installation targets React / Next.js (and, for Vite,
the React + TypeScript template). This project uses Vue 3.

Direct CLI installation (`npx farsiui@latest init`) would introduce React into
a Vue project, which is unacceptable.

## Decision

Adopt a **"reference + manual port"** strategy:

1. Use FarsiUI as a design and code reference (read component source, copy
   markup, Tailwind classes, and RTL logic).
2. Manually port each needed component into a Vue SFC under
   `frontend/src/shared/ui/farsiui/`.
3. Preserve FarsiUI's visual and behavioral contract:
   - RTL layout (`dir="rtl"`, `lang="fa"`).
   - Persian labels (ایمیل, رمز عبور, ورود, ثبت‌نام, فراموشی رمز عبور).
   - Vazirmatn font loaded globally.
   - Tailwind `rtl:` variants where directional styles are needed.
4. Do **not** run `npx farsiui@latest init` in the Vue project root.
5. Do **not** add React as a dependency.
6. The authentication UI must follow the FarsiUI authentication demo
   (https://farsiui-examples.vercel.app/examples/authentication) visually and
   behaviorally.

Any change to this approach requires a new ADR.

## Alternatives considered

- **Install FarsiUI CLI and use React components.** Rejected: introduces
  React into a Vue bundle; violates the Vue 3 baseline.
- **Use a Vue-specific RTL library (e.g., Vuetify).** Rejected: does not match
  FarsiUI's design language; FarsiUI is the explicit choice for this project.
- **Build custom Persian UI components from scratch.** Rejected: duplicated
  effort; FarsiUI provides a strong reference.

## Consequences

- Each ported component must be reviewed for RTL correctness.
- FarsiUI updates are not automatically received; ports are manual.
- Documentation in `docs/FARSIUI_GUIDE.md` must be maintained.
- Tests must verify RTL direction, Persian labels, and Vazirmatn font load.

## References

- docs/FARSIUI_GUIDE.md
- AGENTS.md §8 (frontend rules)
- F-002 (identity) — login/registration UI
