ifneq (,$(wildcard ./.env))
include .env
export
ENV_FILE_PARAM = --env-file .env

endif

build:
	docker compose up --build -d --remove-orphans

up:
	docker compose up -d

down:
	docker compose down

show-logs:
	docker compose logs

migrate:
	docker compose exec api python3 manage.py migrate

makemigrations:
	docker compose exec api python3 manage.py makemigrations

manage-db:
	docker exec -it postgres-db psql -U ${PG_USER} -d ${POSTGRES_DB}

superuser:
	docker compose exec api python3 manage.py createsuperuser

collectstatic:
	docker compose exec api python3 manage.py collectstatic --no-input --clear

startapp:
ifndef name
	@echo "Error: Please provide an app name using 'make startapp name=your_app_name'"
	@exit 1
endif
	docker compose exec api python3 manage.py startapp $(name)
	@echo "Created new app: $(name) in apps/$(name)"
	@echo "Don't forget to add 'apps.$(name)' to INSTALLED_APPS in settings.py"

down-v:
	docker compose down -v

volume:
	docker volume inspect kpl-fantasy-league_postgres_data

fpl-db:
	docker compose exec postgres-db psql --username=root --dbname=fpl

test:
	docker compose exec api pytest -p no:warnings --cov=.

test-html:
	docker compose exec api pytest -p no:warnings --cov=. --cov-report html

flake8:
	docker compose exec api flake8 .
	
black-check:
	docker compose exec api black --check --exclude='migrations|venv' .

black-diff:
	docker compose exec api black --diff --exclude='migrations|venv' .

black:
	docker compose exec api black --exclude='migrations|venv' .


isort-check:
	docker compose exec api isort . --check-only --skip env --skip migrations --skip venv

isort-diff:
	docker compose exec api isort . --diff --skip env --skip migrations --skip venv

isort:
	docker compose exec api isort . --skip env --skip migrations --skip venv
