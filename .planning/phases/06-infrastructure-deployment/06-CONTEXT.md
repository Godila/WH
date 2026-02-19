# Phase 6: Infrastructure & Deployment - Context

**Gathered:** 2026-02-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Deploy the complete WMS system (postgres + backend + frontend) in Docker with healthchecks and automatic restarts. Single command `docker-compose up` brings up all services ready for production use.

</domain>

<decisions>
## Implementation Decisions

### Build Strategy

- **Production-only Dockerfiles** — Development runs outside Docker (uvicorn/npm locally), Docker is for production deployment only
- **Full copy approach** — Simple images with all dependencies, not optimized/minimal (alpine). Prefer simplicity over image size
- **Build on docker-compose up** — Images built when running docker-compose, not pre-built in CI/CD pipeline
- **Dockerfiles in root directory** — `Dockerfile.backend` and `Dockerfile.frontend` in project root, not per-service subdirectories

### OpenCode's Discretion

- Environment variable handling (how to pass DB URL, JWT secret, etc.)
- Database volume strategy and persistence
- Container restart policies and resource limits
- Healthcheck implementation details (endpoints, intervals)
- Logging configuration
- Network configuration between containers

</decisions>

<specifics>
## Specific Ideas

- No specific requirements — standard Docker Compose setup is acceptable

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-infrastructure-deployment*
*Context gathered: 2026-02-19*
