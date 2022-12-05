all: run

run:
	poetry run python Bot/akari.py

dev-setup:
	cp .env-dev-example ./Bot/.env
	cp .env-docker-example .env
	poetry env use 3.11
	poetry install

compose-dev-up:
	sudo docker compose -f docker-compose-dev.yml up -d

compose-dev-stop:
	sudo docker compose -f docker-compose-dev.yml stop