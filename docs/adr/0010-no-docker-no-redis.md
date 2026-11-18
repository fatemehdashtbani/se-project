# ADR-0010: No Docker, No Redis in MVP

- **Status:** Accepted
- **Date:** 2026-11-18
- **Decision owners:** Project team

## Context

The project is a solo/small-team academic-stage build. Docker and Redis add
operational complexity and setup overhead that is not justified at MVP scale.
The professor's constraints explicitly exclude Docker/containers and Redis for
the MVP.

## Decision

**Local development:**
- No Docker, no docker-compose, no Kubernetes.
- Backend runs in a Python virtual environment (`venv` / `poetry`).
- Frontend runs via `npm`/`pnpm` with Vite.
- PostgreSQL installed natively (or via a managed instance for CI) for
  integration tests; SQLite used for fast unit tests.

**Runtime:**
- No Redis, no external cache, no message broker in MVP.
- Caching (if needed) uses in-process Python structures (e.g., `functools.lru_cache`,
  `cachetools`) with clear invalidation.
- Background work uses FastAPI BackgroundTasks (see ADR-0011).

**Deployment:**
- Native deployment: process manager (systemd) + reverse proxy (nginx) or a
  PaaS that supports Python and Node without containers.
- CI (GitHub Actions) runs tests directly with Python and Node, no Docker
  service.

**Revisit conditions:**
- Introducing Docker or Redis requires a new ADR supported by a concrete
  operational need (scale, cache pressure, background job durability).

## Alternatives considered

- **Docker for local parity.** Rejected: violates project constraint;
  native setup is sufficient for a small team.
- **Redis for sessions/cache.** Rejected: JWT strategy (ADR-0005) is
  stateless; cache needs are minimal.
- **Redis for background jobs (Celery/RQ).** Rejected: FastAPI
  BackgroundTasks (ADR-0011) suffices at MVP scale.

## Consequences

- Local setup is simpler and faster.
- CI must run native test steps (no docker-in-docker).
- Session state must remain client-carried (JWT) or DB-backed; no Redis
  sessions.
- When scale demands a queue or cache, revisit via ADR.

## References

- AGENTS.md §3 (tech baseline)
- ARCHITECTURE.md §3, §18
- ADR-0002 (database environments)
- ADR-0011 (background tasks)
