#!/usr/bin/env bash
set -e

: "${APP_DB_USER:?APP_DB_USER must be set}"
: "${APP_DB_PASSWORD:?APP_DB_PASSWORD must be set}"
: "${APP_DB_SCHEMA:=app}"

echo "Creating PostgreSQL application user: ${APP_DB_USER}"

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set ON_ERROR_STOP=1 \
  --set app_user="$APP_DB_USER" \
  --set app_password="$APP_DB_PASSWORD" \
  --set app_schema="$APP_DB_SCHEMA" <<'SQL'

SELECT format(
  'CREATE ROLE %I LOGIN PASSWORD %L',
  :'app_user',
  :'app_password'
)
WHERE NOT EXISTS (
  SELECT FROM pg_roles WHERE rolname = :'app_user'
)
\gexec

SELECT format(
  'ALTER ROLE %I WITH LOGIN PASSWORD %L',
  :'app_user',
  :'app_password'
)
\gexec

SELECT format(
  'CREATE SCHEMA IF NOT EXISTS %I AUTHORIZATION %I',
  :'app_schema',
  :'app_user'
)
\gexec

SELECT format(
  'GRANT CONNECT ON DATABASE %I TO %I',
  current_database(),
  :'app_user'
)
\gexec

SELECT format(
  'GRANT USAGE, CREATE ON SCHEMA %I TO %I',
  :'app_schema',
  :'app_user'
)
\gexec

SQL

echo "PostgreSQL application user initialized."