# Fieldwork — backend

FastAPI + PostgreSQL half of Fieldwork, a project tracker. Split out from a
single-repo layout into its own repo so Holodeck can target it independently
of the frontend — a ticket scoped to this repo produces a backend-only PR,
not one touching both halves.

The frontend lives in a separate repo (`test_frontend`) and talks to this
service over `/api`.

## Run standalone

```bash
docker compose up -d --build
```

- API: http://localhost:18000
- OpenAPI docs: http://localhost:18000/docs
- Health: http://localhost:18000/api/health

PostgreSQL is not exposed on a host port by default — only reachable from
`backend` on the compose network.

## Configuration

```bash
cp env.example .env
```

- `BACKEND_PORT`: host port, default `18000`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: database initialization
- `DATABASE_URL`: backend connection string
- `CORS_ORIGINS`: comma-separated browser origins allowed to call `/api` directly
  (set this to wherever `test_frontend` is running if you're testing both
  repos standalone side by side, e.g. `http://localhost:13000`)

If database credentials change after the volume has been initialized, reset
the volume before restarting (`docker compose down --volumes`).

## Data model

- `projects`, `members`, `labels`, `tasks`, `task_labels` (many-to-many)

Deleting a project also deletes its tasks. Deleting a member leaves assigned
tasks in place and clears their assignee.

## API

CRUD endpoints for `/api/projects`, `/api/members`, `/api/labels`,
`/api/tasks`. Supporting endpoints: `GET /api/dashboard/summary`,
`GET /api/health`. Full contract in Swagger UI at `/docs`.

## Common commands

```bash
make up       # build and start
make logs     # follow logs
make ps       # show health
make down     # stop, keep data
make reset    # stop and delete database data
```

Apply migrations manually:

```bash
docker compose run --rm backend alembic upgrade head
```

## Extend

Code is grouped into SQLAlchemy models, Pydantic schemas, and API routes
under `app/`. Add schema changes through a new Alembic revision under
`alembic/versions/`.

## Move the repository

Copy this directory to another machine with Docker and run
`docker compose up -d --build`. Nothing outside this repo is required to run
the backend + its own database standalone (the frontend is a separate
concern, in its own repo).
