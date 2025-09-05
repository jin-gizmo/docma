#!/bin/bash

# Create the docma user. We do this as a shell script not an SQL as we want to use
# environment vars from .env.

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-!
DO
\$do\$
    BEGIN
        IF
            EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${PGLOCAL_USER}') THEN
            RAISE NOTICE 'Role "${PGLOCAL_USER}" already exists. Skipping.';
        ELSE
            CREATE ROLE ${PGLOCAL_USER} LOGIN PASSWORD '${PGLOCAL_PASSWORD}';
        END IF;
    END
\$do\$;
!
