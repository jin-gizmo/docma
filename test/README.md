# Testing

This directory provides the docker setup to run a local Postgres instance to
teat database access stuff.

> This is a cutdown version of the lava test rig.

## Local Test Environment

...

## Setup

### Environment

The docker containers rely on some environment variables that should be set in
a `.env` file in the `test` directory. The best way to do this is to create
the `.env` file in the docma main directory and create a symlink to it from the
`test` directory. This allows the sample templates to access the database.

This is done to avoid passwords being committed to the repo. There is no
sensitive data in the database, just some simple sample data but it's still
good practice.

The `.env` file should look like this:

```bash
PGADMIN_USER=master
PGADMIN_PASSWORD=...

PGLOCAL_USER=docma
PGLOCAL_PASSWORD=...
PGLOCAL_HOST=localhost
PGLOCAL_PORT=5432
PGLOCAL_DATABASE=docma
```

## Connecting to the Local Service Containers

The docker compose process described above will create a suite of local services
(e.g. database engines, SMB server) all connected to a common docker network.

These are available at the following endpoints.

| Service    | Port | Access from host | Access from docker network |
|------------|------|------------------|----------------------------|
| PostgreSQL | 5432 | localhost        | lava-test-postgres         |

In order for the same hostnames to be used to access these, both from the
host and from within another container on the docker network, the following
entries should be added to /ets/hosts on the host.

```
127.0.0.1   docma-test-postgres
```
