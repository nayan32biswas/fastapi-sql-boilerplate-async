# Fastapi SQL boilerplate

Build the docker images

```bash
docker-compose build
```

Run Migration

```bash
docker-compose run server alembic upgrade head
```

Run Backend server

```bash
docker-compose up server
```

Run pytest

```bash
docker-compose run --rm server ./scripts/test.sh
```

## Example Command

Create Migration Script

```bash
docker-compose run server alembic revision --autogenerate -m "message"
```
