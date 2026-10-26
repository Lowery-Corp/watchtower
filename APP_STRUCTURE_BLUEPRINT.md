# Watchtower Application Structure Blueprint

This document maps the current repository, service boundaries, active routes,
data model, runtime flows, and known integration gaps for Watchtower. It is a
contributor reference for the React frontend, FastAPI API, PostgreSQL,
Redis, external auth service, and Docker Compose stack.

The document describes the checkout as it exists today. It separates active
behavior from scaffolding, unused dependencies, and code that is present but
not currently wired into a working flow.

## Technology summary

| Area | Technology |
| --- | --- |
| Frontend | React 19.1, Vite 7.1, JavaScript with JSX, CSS |
| API | Python 3.12, FastAPI 0.135, Uvicorn, Pydantic 2 |
| HTTP client | HTTPX 0.28 with Tenacity retry policy |
| Persistence | PostgreSQL 17-compatible `pgvector/pgvector:pg17`, SQLAlchemy 2 async, Alembic |
| Cache | Redis (`redis:latest`) with the async Redis client |
| Authentication | External auth API plus HTTP-only cookie at the Watchtower boundary |
| Local orchestration | Docker Compose |

`backend/requirements.txt` contains additional packages for Celery, MinIO,
MCP, PDF processing, and other integrations, but no active Watchtower module
currently uses those capabilities.

## Repository layout

```text
watchtower/
├── README.md
├── AGENTS.md
├── APP_STRUCTURE_BLUEPRINT.md
├── LICENSE
├── .gitignore
├── docker-compose.yaml
├── postgres/
│   └── init/
│       └── 01-create-app-user.sh
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   ├── README
│   │   └── versions/fa71fa6e66ff_init_login_log.py
│   ├── api/v1/
│   │   ├── api.py
│   │   └── endpoints/{auth,health}.py
│   ├── auth/dependencies.py
│   ├── cache/{redis,dependencies,helpers}.py
│   ├── core/{config,retry}.py
│   ├── db/{base,session,dependencies}.py
│   ├── httpxC/http_client.py
│   ├── middleware/request_id.py
│   ├── models/login_log.py
│   ├── repositories/{auth,user,jwt_token_blacklist}.py
│   └── schemas/user.py
└── frontend/
    ├── index.html
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── .env.example
    └── src/{main,App,index}.jsx/css
```

## Runtime topology

```text
Browser :5173
  |
  | VITE_API_URL (default: http://localhost:8000)
  v
FastAPI backend :8000
  |        |         |
  |        |         `--> external AUTH_API_URL
  |        |              - login
  |        |              - current user
  |        |              - logout/revocation
  |        |              - user creation
  |        |
  |        `--> Redis cache :6379
  |
  `----------> PostgreSQL :5432
                - app.login_log
                - app.alembic_version
```

Docker Compose defines the services `frontend`, `backend`, `postgres`, and
`cache`. The frontend and backend publish ports 5173 and 8000 by default;
PostgreSQL and Redis publish 5432 and 6379. Named volumes retain frontend
`node_modules`, Redis data, and PostgreSQL data.

Compose starts `backend` after PostgreSQL reports healthy and starts
`frontend` after the backend reports healthy. The backend's FastAPI lifespan
also pings Redis before yielding, but Compose does not currently express a
`cache` health dependency for `backend`.

## Root files

| Path | Responsibility |
| --- | --- |
| `README.md` | Setup, API snapshot, development notes, and local runbook. |
| `AGENTS.md` | Repository-specific change, verification, and security instructions. |
| `APP_STRUCTURE_BLUEPRINT.md` | This architecture and ownership reference. |
| `docker-compose.yaml` | Builds the frontend/backend and wires PostgreSQL, Redis, ports, volumes, and health checks. |
| `postgres/init/01-create-app-user.sh` | Creates/updates the configured application role and `app` schema on first database initialization. |
| `LICENSE` | MIT license. |
| `.gitignore` | Ignores environment files, dependencies, build output, caches, and local database artifacts. |

## Compose services

| Service | Image/build | Published port | Runtime role |
| --- | --- | --- | --- |
| `frontend` | `frontend/Dockerfile` / Node 22 Alpine | `${FRONTEND_PORT:-5173}:5173` | Vite dev server with a bind-mounted source tree. |
| `backend` | `backend/Dockerfile` / Python 3.12 slim | `${BACKEND_PORT:-8000}:8000` | Reload-mode Uvicorn process serving FastAPI. |
| `postgres` | `pgvector/pgvector:pg17` | `${POSTGRES_PORT:-5432}:5432` | Application database and migration target. |
| `cache` | `redis:latest` | `${REDIS_PORT:-6379}:6379` | Redis server with persistence disabled by command flags. |

The backend and frontend require `backend/.env` and `frontend/.env`; Compose
also reads the root `.env` for PostgreSQL and interpolation. Only environment
examples are committed. The backend settings currently require
`DATABASE_URL`, `REDIS_URL`, `COOKIE_KEY`, and `AUTH_API_URL`.

## Frontend

The frontend is intentionally a single-page starter screen. It mounts React in
`main.jsx`, imports `index.css`, and renders `App.jsx`.

| Path | Responsibility |
| --- | --- |
| `frontend/index.html` | Vite document shell; title is currently `New App`. |
| `frontend/src/main.jsx` | React 19 `createRoot` entry point with `StrictMode`. |
| `frontend/src/App.jsx` | Displays the starter hero and a link to the API health endpoint. |
| `frontend/src/index.css` | Global dark theme, layout, and button styling. |
| `frontend/vite.config.js` | Enables the React Vite plugin. |
| `frontend/package.json` | `dev`, `build`, and `preview` scripts plus React/Vite dependencies. |

There is no frontend router, API client module, authentication state, form, or
application page beyond the starter screen. `VITE_API_URL` is read at build or
dev-server startup and defaults to `http://localhost:8000`.

## Backend structure

`backend/main.py` creates the FastAPI application, starts and stops the shared
Redis manager and HTTPX client through the lifespan, installs request-ID and
credentialed CORS middleware, and mounts the v1 router at `/api/v1`.

| Path | Responsibility |
| --- | --- |
| `api/v1/endpoints/` | HTTP handlers for auth and health. |
| `auth/` | Cookie-to-user dependency and an admin API-key guard scaffold. |
| `cache/` | Redis pool lifecycle, FastAPI dependencies, and JSON serialization helper. |
| `core/` | Environment-backed settings and retry policy for transient HTTP failures. |
| `db/` | SQLAlchemy metadata, async engine/session, and FastAPI session dependency. |
| `httpxC/` | Shared async HTTPX client with bounded timeouts and connection limits. |
| `middleware/` | Adds a UUID `X-Request-ID` to each response. |
| `models/` | SQLAlchemy models in the `app` schema. |
| `repositories/` | External auth calls, user login orchestration, and blacklist placeholders. |
| `schemas/` | Pydantic input/output models and validation. |
| `alembic/` | Async migration environment and migration history. |

## Active API routes

Every route is prefixed with `/api/v1`.

| Method | Route | Handler | Authentication | Behavior |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | `health_check` | None | Returns `{"status":"ok"}`. |
| `GET` | `/health/ready` | `readiness_check` | None | Returns static `{"status":"ready"}`. |
| `GET` | `/health/live` | `liveness_check` | None | Returns alive status and UTC timestamp. |
| `POST` | `/auth/login` | `login_route` | Credentials in body | Delegates login, sets the configured cookie, and returns the username. Errors are converted to a 401 response body. |
| `GET` | `/auth/me` | `read_me_route` | Cookie dependency | Resolves the cookie through the upstream auth API and returns the username. |
| `POST` | `/auth/logout` | `logout_route` | Cookie if present | Delegates logout/revocation and deletes the `access_token` cookie. |
| `POST` | `/auth/register` | `register_route` | None | Attempts to create a user through the upstream auth API. |

## Authentication flow

```text
Browser
  |
  | POST /api/v1/auth/login { username, password }
  v
Watchtower login_route
  |
  | POST AUTH_API_URL/api/v1/auth/login { email, password, internal: true }
  v
External auth service
  |
  `--> token
Watchtower
  |
  +--> sets COOKIE_KEY as HttpOnly, Secure, SameSite=Lax, one-hour cookie
  `--> returns { username }
```

For `/auth/me`, `get_current_user` reads the cookie and
`repositories.auth.get_user_from_token` sends it to the upstream `/auth/me`
endpoint in a custom `token` header. Logout sends the same token as a Bearer
header to the upstream logout endpoint. HTTP calls use the shared HTTPX client
and retry transient connection/time-out and 5xx failures twice.

## Schemas and persistence

`schemas/user.py` defines `UserCreate`, `UserLogin`, `DeleteUser`, `UserToken`,
`LoginResponse`, and `AuthorizedUser`. Email-like identifiers are normalized to
lowercase at the schema boundary. New-user passwords require at least eight
characters, a letter, a digit, and a configured special character.

The SQLAlchemy metadata and Alembic version table use the PostgreSQL `app`
schema. The checked-in migration `fa71fa6e66ff_init_login_log.py` creates:

### `app.login_log`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | Integer | Auto-incrementing primary key. |
| `user_id` | UUID | Indexed; not a declared foreign key. |
| `login_datetime` | Timestamp with timezone | Indexed. |

The model is imported into `db.base` for Alembic discovery. The current login
route does not insert rows into this table, so it is schema scaffolding rather
than an active audit flow.

## Known integration gaps

These are observed facts about the current checkout, not planned behavior:

1. **Environment bootstrap is incomplete.** Compose references a root `.env`,
   `backend/.env`, and `frontend/.env`, but only the two example files are
   tracked. The examples do not provide all required settings.
2. **Settings and consumers are out of sync.** `auth/dependencies.py` reads
   `settings.scrappys_api_key`, while `core/config.py` does not define it.
   `internal_api_login` also references settings fields that are not declared.
3. **Registration schema mismatch.** `UserCreate` exposes `username`, while
   `register_route` reads `new_user.email`; the route will fail before a valid
   registration request reaches the external auth API.
4. **Cookie-key mismatch on logout.** Login/dependency code uses configurable
   `COOKIE_KEY`, but logout deletes the literal `access_token` cookie.
5. **Redis startup ordering is implicit.** FastAPI pings Redis at startup, but
   backend Compose dependencies only wait for PostgreSQL.
6. **Container and host ports differ.** Backend-to-cache traffic must use
   `cache:6379`; the `REDIS_PORT` variable controls only the host-published
   port and should not be used for container-to-container traffic.
7. **Health is shallow.** Readiness does not check PostgreSQL, Redis, or the
   external auth service.
8. **Database work is only partially wired.** SQLAlchemy sessions and the
   `login_log` migration exist, but authentication is delegated upstream and
   no login event is recorded by the active route.
9. **Unused scaffolding remains.** The admin guard, blacklist repository,
   Celery-related dependencies, and several broad requirements are not active
   application flows.
10. **No automated tests are checked in.** Verification currently relies on
   static inspection, compilation/build checks, and manual Compose/API checks.

When closing any of these gaps, update this document, the README, the relevant
environment examples, and migrations or tests as appropriate.
