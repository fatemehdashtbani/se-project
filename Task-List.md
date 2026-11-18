# Task List — Routine Manager

> **Rules**
> - Every new feature is **registered here first** (status: `Backlog`) before any
>   work begins.
> - Feature folder name: `docs/features/<NNN>-<slug>/`.
> - Every feature must have `SPEC.md` + `PLAN.md` linked before status becomes
>   `In Progress`.
> - Every architectural decision is an ADR in `docs/adr/`.
> - Update this file **in the same commit** as the state change.

Legend: 🟦 Backlog · 🟨 In Progress · 🟪 In Review · 🟩 Done · 🔴 Blocked

---

## 📌 Backlog

| ID  | Feature | SPEC | PLAN | ADRs | Status | Notes |
|-----|---------|------|------|------|--------|-------|
| 001 | User Authentication (sign-up/login/JWT) | docs/features/001-user-auth/SPEC.md | docs/features/001-user-auth/PLAN.md | 0003 | 🟦 Backlog | Foundation for everything |
| 002 | RBAC & Roles (User/Mentor/Admin) | docs/features/002-rbac/SPEC.md | docs/features/002-rbac/PLAN.md | TBD | 🟦 Backlog | Depends on 001 |
| 003 | Routine CRUD | docs/features/003-routine-crud/SPEC.md | docs/features/003-routine-crud/PLAN.md | TBD | 🟦 Backlog | Core domain |
| 004 | Routine Scheduling (recurring) | docs/features/004-routine-scheduling/SPEC.md | docs/features/004-routine-scheduling/PLAN.md | TBD | 🟦 Backlog | Needs 003 |
| 005 | Check-in Tracking | docs/features/005-check-in-tracking/SPEC.md | docs/features/005-check-in-tracking/PLAN.md | TBD | 🟦 Backlog | Needs 003 |
| 006 | Dashboard & Analytics | docs/features/006-dashboard/SPEC.md | docs/features/006-dashboard/PLAN.md | TBD | 🟦 Backlog | Needs 005 |
| 007 | Reminders & Notifications (email + push) | docs/features/007-notifications/SPEC.md | docs/features/007-notifications/PLAN.md | TBD | 🟦 Backlog | Needs 005 |
| 008 | Mentor Discovery & Selection | docs/features/008-mentor-discovery/SPEC.md | docs/features/008-mentor-discovery/PLAN.md | TBD | 🟦 Backlog | Needs 002 |
| 009 | Mentor Access (consent-based) | docs/features/009-mentor-access/SPEC.md | docs/features/009-mentor-access/PLAN.md | TBD | 🟦 Backlog | Needs 002, 003, 008 |
| 010 | Mentor Messaging & Comments | docs/features/010-mentor-messaging/SPEC.md | docs/features/010-mentor-messaging/PLAN.md | TBD | 🟦 Backlog | Needs 009 |
| 011 | Subscription Plans (Free/Paid) | docs/features/011-subscriptions/SPEC.md | docs/features/011-subscriptions/PLAN.md | TBD | 🟦 Backlog | Needs 002 |
| 012 | Admin Panel (web only) | docs/features/012-admin-panel/SPEC.md | docs/features/012-admin-panel/PLAN.md | TBD | 🟦 Backlog | Needs 002, 011 |
| 013 | Android App | docs/features/013-android-app/SPEC.md | docs/features/013-android-app/PLAN.md | 0004 | 🟦 Backlog | **Blocked on ADR-0004** (tech stack) |
| 014 | Team / Group Routines | docs/features/014-team-routines/SPEC.md | docs/features/014-team-routines/PLAN.md | TBD | 🟦 Backlog | Optional, future |

---

## 🟨 In Progress

| ID  | Feature | SPEC | PLAN | ADRs | Status | Owner | Started |
|-----|---------|------|------|------|--------|-------|---------|
| —   |         |      |      |      |        |       |         |

---

## 🟪 In Review

| ID  | Feature | PR  | Status | Reviewer |
|-----|---------|-----|--------|----------|
| —   |         |     |        |          |

---

## 🟩 Done

| ID  | Feature | Merged | ADRs |
|-----|---------|--------|------|
| —   |         |        |      |

---

## 🚫 Blocked

| ID  | Feature | Blocked By | Reason |
|-----|---------|------------|--------|
| 013 | Android App | ADR-0004 | Mobile tech stack not yet decided |

---

## 📚 ADR Index

| ADR  | Title | Status | Date |
|------|-------|--------|------|
| 0001 | Record architecture decisions | Accepted | TBD |
| 0002 | Use FastAPI + async SQLAlchemy | Proposed | TBD |
| 0003 | Choose JWT over server sessions | Proposed | TBD |
| 0004 | Mobile tech stack (Flutter/RN/Kotlin) | **TBD** | — |
| 0005 | RBAC model & storage | TBD | — |
| 0006 | Consent-based mentor access model | TBD | — |

> Keep this index in sync with `docs/adr/`.

---

## 📝 How to add a new feature (checklist)

1. [ ] Add a row to **Backlog** with a unique ID (`NNN`) and a slug.
2. [ ] Create `docs/features/NNN-<slug>/SPEC.md` from the template in
       `AGENTS.md §16.2`.
3. [ ] Create `docs/features/NNN-<slug>/PLAN.md` from the template in
       `AGENTS.md §16.3`.
4. [ ] Write ADR(s) for architectural decisions introduced
       (`docs/adr/NNNN-title.md`, `AGENTS.md §16.1`).
5. [ ] Move the row to **In Progress** and set Owner + Started.
6. [ ] Branch `feature/NNN-<slug>` and implement with TDD.
7. [ ] Open PR → **In Review**.
8. [ ] Merge → move to **Done**, set Merged date.
