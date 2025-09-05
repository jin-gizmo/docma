
.PHONY: help init start stop unit

# ------------------------------------------------------------------------------
help:
	@echo
	@echo "[31m--------------------------------------------------------------------------------"
	@echo " STOP: You should really be doing this from the base directory rather than here "
	@echo "--------------------------------------------------------------------------------[0m"
	@echo
	@echo What do you want to make?  Available targets are:
	@echo
	@echo "   help:         Print this help text."
	@echo "   init:         Initialise test environment."
	@echo "   start/up:     Start the docker containers providing test resources."
	@echo "   stop/down:    Stop the docker containers providing test resources."
	@echo "   test:         Run the unit tests."
	@echo "   coverage:     Run the unit tests and produce a coverage report."
	@echo "   clean:        Remove ephemeral junk (orphan docker volumes etc)."
	@echo


init:	duckdb

duckdb: services/duckdb/test.db

up:	start

down:	stop

start:	duckdb
	docker compose up --renew-anon-volumes -d

stop:
	docker compose down --volumes

test:
	pytest -v -s

coverage:
	pytest --cov=.. --cov-report html:../dist/test/htmlcov


clean:
	docker system prune -f
	docker volume prune -f
	docker network prune -f

services/duckdb/test.db:
	cat services/duckdb/init.d/*.sql | duckdb $@
