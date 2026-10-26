# Inventory Api

Generated from the FastAPI/Postgres/Redis blueprint.

## Start locally

```bash
docker compose up --build
```

The frontend is available at `http://localhost:5173` and the API at `http://localhost:8011`.

Run migrations from the backend container when needed:

```bash
docker compose exec backend alembic upgrade head
```
