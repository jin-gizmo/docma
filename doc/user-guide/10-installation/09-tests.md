## Running Unit Tests

The unit tests require some docker based components (Postgres, web server etc.)
to be up and running. These require a `.env` file containing credentials for
test accounts etc. In the main directory, copy `dot-env-sample` to `.env` and
edit it to add passwords in the indicated spots. The values don't really matter
as the accounts will be created as part of each test session. Even so, **do
not** add `.env` to the repo. It's bad form.

To run the tests:

```bash
# Start the docker components. This will take a while on first invocation as it
# needs to download base images and build some stuff on them.
make up

# Run tests 
make test

# Get a coverage report 
make coverage

# Check the coverage report (on a Mac)
open -a Safari dist/test/htmlcov/index.html

# Stop the docker components when done
make down
```
