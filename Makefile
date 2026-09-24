.PHONY: up down build logs ps reset

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

ps:
	docker compose ps

reset:
	docker compose down --volumes --remove-orphans
