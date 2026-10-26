# Repository Agent Instructions

## Scope

These instructions apply to the entire Watchtower repository. Read them before
editing application code, infrastructure, or documentation.

## Project shape

- `backend/` is a Python 3.12 FastAPI service. Keep imports compatible with
  the container's `/app` working directory.
- `frontend/` is a Vite React application using JavaScript/JSX. Do not add a
  framework or router without updating the blueprint and README.
- PostgreSQL and Redis are local Compose dependencies. Container-to-container
  URLs must use Compose service names (`postgres`, `cache`), not host
  `localhost`.
- Authentication is delegated to `AUTH_API_URL`; Watchtower owns the browser
  cookie boundary and request orchestration, not the upstream user database.

## Safe change workflow

1. Inspect the existing route, repository, schema, and configuration path
   before changing behavior.
2. Preserve the current API prefix (`/api/v1`) and cookie/CORS semantics unless
   the change explicitly updates the public contract.
3. Add or update an Alembic migration for every persisted-schema change. Keep
   models and migrations in the same schema (`app`).
4. Update `README.md` and `APP_STRUCTURE_BLUEPRINT.md` when adding routes,
   services, environment variables, Compose dependencies, or user-visible
   behavior.
5. Never commit `.env` files, credentials, tokens, generated frontend output,
   dependency directories, or database volumes.

## Verification

Use the narrowest relevant checks available in the environment:

```bash
python -m compileall backend
npm --prefix frontend run build
docker compose config
```

If a check cannot run because dependencies or environment files are absent,
report that fact rather than claiming success. There is currently no test suite;
new behavior should add focused tests before being described as covered.

## Security and integration guardrails

- Keep auth tokens in HTTP-only cookies or explicit authorization headers; do
  not log token values.
- Treat the upstream auth API as an external dependency. Use the existing
  retry policy only for transient HTTP failures and preserve meaningful error
  handling for authentication failures.
- Keep CORS origins explicit. Do not use `*` with credentials enabled.
- Validate and normalize user identifiers at the schema boundary.
- Treat the scaffold's known gaps as real until they are fixed and verified;
  do not silently document planned behavior as active behavior.

## Documentation convention

`APP_STRUCTURE_BLUEPRINT.md` is the source of truth for repository inventory,
runtime topology, active routes, persistence, flows, and limitations. Keep its
diagrams and tables factual to the current checkout.
