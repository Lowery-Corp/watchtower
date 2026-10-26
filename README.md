# Watchtower

Watchtower is a small full-stack scaffold for an authenticated web application.
It currently contains a Vite/React landing page, a FastAPI API, PostgreSQL
metadata and migrations for login events, Redis connectivity, and an HTTP
client for delegating authentication to an external auth service.

The repository is an active scaffold rather than a finished product. The
current implementation and its known integration gaps are recorded in
[`APP_STRUCTURE_BLUEPRINT.md`](APP_STRUCTURE_BLUEPRINT.md).

## Stack

- **Frontend:** React 19, Vite 7, Tailwind CSS 4, JavaScript/JSX
- **API:** Python 3.12, FastAPI, Uvicorn, Pydantic Settings
- **Persistence:** PostgreSQL 17 (`pgvector/pgvector` image), SQLAlchemy 2,
  Alembic, `app` schema
- **Cache:** Redis
- **Authentication:** delegated to the configured external auth API; the API
  stores the returned token in an HTTP-only cookie
- **Local orchestration:** Docker Compose

## Repository map

```text
watchtower/
├── README.md
├── AGENTS.md
├── APP_STRUCTURE_BLUEPRINT.md
├── docker-compose.yaml
├── docker-compose.deploy.yml
├── .github/workflows/deploy.yml
├── postgres/init/01-create-app-user.sh
├── backend/
│   ├── main.py
│   ├── api/v1/endpoints/{auth,health}.py
│   ├── auth/                 # cookie authentication dependency
│   ├── cache/                # Redis lifecycle and JSON helper
│   ├── core/                 # settings and HTTP retry policy
│   ├── db/                   # SQLAlchemy engine/session/metadata
│   ├── models/               # login_log model
│   ├── repositories/         # external auth calls and token stubs
│   ├── schemas/              # request/response validation
│   ├── middleware/           # X-Request-ID middleware
│   └── alembic/              # migration environment and revisions
└── frontend/
    ├── index.html
    └── src/{main,App,index}.jsx/css
```

## Run locally with Docker Compose

Docker Compose expects three environment files that are intentionally not
committed:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# create the root .env from the example below; no root example is committed yet
```

At minimum, configure the values required by `backend/core/config.py` and the
PostgreSQL init script. A working local configuration includes:

```dotenv
# .env (Compose/PostgreSQL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=watchtower
APP_DB_USER=watchtower
APP_DB_PASSWORD=watchtower
APP_DB_SCHEMA=app
POSTGRES_PORT=5432
REDIS_PORT=6379

# backend/.env (container-local settings)
DATABASE_URL=postgresql+asyncpg://watchtower:watchtower@postgres:5432/watchtower
REDIS_URL=redis://cache:6379/0
COOKIE_KEY=access_token
AUTH_API_URL=https://auth.example.invalid

# frontend/.env
VITE_API_URL=http://localhost:8000
```

Then start the services:

```bash
docker compose up --build
```

The frontend is available at `http://localhost:5173` by default and the API at
`http://localhost:8000`. This checkout uses `FRONTEND_PORT=5174` and
`BACKEND_PORT=8011` in its local `.env`, so its live URLs are
`http://localhost:5174` and `http://localhost:8011`. The frontend's **Check API health** link calls
`GET /api/v1/health`.

Apply the checked-in migration from the backend container when the database is
ready:

```bash
docker compose exec backend alembic upgrade head
```

To stop the stack while preserving named volumes:

```bash
docker compose down
```

## API snapshot

All routes are under `/api/v1`:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Basic process health (`{"status":"ok"}`). |
| `GET` | `/health/ready` | Static readiness response. |
| `GET` | `/health/live` | Alive response with a UTC timestamp. |
| `POST` | `/auth/login` | Delegates login to `AUTH_API_URL`, then sets the cookie. |
| `GET` | `/auth/me` | Resolves the cookie through the external auth API. |
| `POST` | `/auth/logout` | Delegates token revocation and deletes the cookie. |
| `POST` | `/auth/register` | Delegates account creation to the external auth API. |

The backend also adds an `X-Request-ID` response header to every request and
allows credentialed CORS requests from the configured frontend origins in
`backend/main.py`.

## Development notes

- There are currently no automated tests in the repository.
- The Compose files reference `.env` files, but only the backend and frontend
  examples are checked in; create the root file and local copies before
  starting Compose.
- Redis is connected during FastAPI startup, and Compose now waits for the
  `cache` health check before starting the backend.
- Inside Compose, use the cache service's internal port (`cache:6379`) in
  `REDIS_URL`; `REDIS_PORT` only controls the host-published port.
- Readiness is currently a static response and does not verify PostgreSQL or
  Redis.
- The database migration creates `app.login_log`; the current login route does
  not write to that table.
- The external auth contract still needs valid upstream credentials and route
  behavior before registration or login can succeed end to end. See the
  blueprint's **Known integration gaps** section.

## Contribution guidance

Read [`AGENTS.md`](AGENTS.md) before making changes. Keep the architecture
blueprint current when adding routes, services, models, environment variables,
or Compose dependencies.

## Production deployment

`.github/workflows/deploy.yml` follows the Vaults deployment pattern. On pushes
to `main`, it builds and pushes immutable API and frontend images to Docker Hub,
connects to the deployment host over Tailscale SSH, copies the Compose files,
and starts the production stack with `docker-compose.deploy.yml`.

Configure these GitHub Actions secrets in the `build and deploy` environment:

- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`
- `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY`, `SERVER_APP_DIR`

Before the first deployment, provision these server-side files in
`SERVER_APP_DIR`: `.env`, `backend/.env`, and `frontend/.env`. They contain
database credentials, the external auth URL, and the browser-facing
`VITE_API_URL`; they are intentionally not copied from GitHub. The deployment
override removes development bind mounts, pulls the commit-tagged images, runs
`alembic upgrade head`, and verifies `/api/v1/health` before the workflow exits.

## License

MIT. See [`LICENSE`](LICENSE).
