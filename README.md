# Fastapi SQL boilerplate

Build the docker images

`docker-compose build`

Create Migration Script

`docker-compose run server alembic revision --autogenerate -m "message"`

Run Migration

`docker-compose run server alembic upgrade head`
