
PYTEST_WORKERS=auto
# PYTEST_WORKERS=4

# This is the name of an index server for twine uploads in ~/.pypirc
pypi=pypi

# ------------------------------------------------------------------------------
HIDDEN_PYTHON=$(shell \
	find . -type f -perm -u=x ! -name '*.py' ! -name '*.sh' ! -path './venv/*' \
			! -path './.??*/*' ! -path './doc/*' ! -path './untracked/*' \
			! -path './dist/*' ! -path './*egg-info*' \
		-print0 | xargs -r -0 file | grep 'Python script' | cut -d: -f1)


.PHONY: black help _venv_is_off _venv_is_on _venv update check cookie doc spell test coverage

DOCMA_VERSION=$(shell cat docma/VERSION)

# Add --progress=plain for debugging
DOCKER_BUILD=docker buildx build

COOKIE_DIR=docma/lib/cookiecutter

# ------------------------------------------------------------------------------
help:
	@echo
	@echo What do you want to make?  Available targets are:
	@echo
	@echo "[31mGetting started[0m"
	@echo "   init:      Initialise / update the project (create venv etc.). Idempotent."
	@echo "   help:      Print this help text."
	@echo
	@echo "[31mBuild / install targets[0m"
	@echo "   all:       Combines pkg, docker and doc"
	@echo "   doc:       Make the user guide."
	@echo "   docker:    Build a docker image with docma installed."
	@echo "   pkg:       Build the Python package."
	@echo "   pypi:      Upload the pkg to the \"$(pypi)\" PyPI server via twine. The"
	@echo "              \"$(pypi)\" server must be defined in ~/.pypirc. Add pypi=..."
	@echo "              to specify a different index server entry in ~/.pypirc."
	@echo
	@echo "[31mMiscellaneous targets[0m"
	@echo "   black      Format the code using black."
	@echo "   check:     Run some code checks (flake8 etc)."
	@echo "   clean:     Remove generated components, fluff etc."
	@echo "   count:     Do line counts on source code (needs tokei)."
	@echo "   spell:     Spell check the user guide (requires aspell)."
	@echo
	@echo "[31mTesting targets[0m"
	@echo "   coverage:  Run the unit tests and produce a coverage report."
	@echo "   test:      Run the unit tests."
	@echo "   start/up:  Start the docker containers providing test resources."
	@echo "   stop/down: Stop the docker containers providing test resources."
	@echo


# ------------------------------------------------------------------------------
# Check virtual environment is not active
_venv_is_off:
	@if [ "$$VIRTUAL_ENV" != "" ] ; \
	then \
		echo Deactivate your virtualenv for this operation ; \
		exit 1 ; \
	fi

_venv_is_on:
	@if [ "$$VIRTUAL_ENV" == "" ] ; \
	then \
		echo Activate your virtualenv for this operation ; \
		exit 1 ; \
	fi
	

# Setup the virtual environment
_venv:	_venv_is_off
	@if [ ! -d venv ] ; \
	then \
		echo Creating virtualenv ; \
		python3 -m venv venv ; \
	fi
	@( \
		echo Activating venv ; \
		source venv/bin/activate ; \
		export PIP_INDEX_URL=$(PIP_INDEX_URL) ; \
		if [ "$(os)" = "amzn2018" -a "$$PYTHON_INSTALL_LAYOUT" = "amzn" ] ; \
		then \
			echo "Aargh - Amazon Linux 1 - pip is broken - unsetting PYTHON_INSTALL_LAYOUT" ; \
			export PYTHON_INSTALL_LAYOUT= ; \
		fi ; \
		echo Installing requirements ; \
		python3 -m pip install 'pip>=20.3' --upgrade ; \
		python3 -m pip install -r requirements.txt --upgrade ; \
		python3 -m pip install -r requirements-build.txt --upgrade ; \
		: ; \
	)

_git:	.git
	git config core.hooksPath etc/git-hooks

# ------------------------------------------------------------------------------
init: 	_venv _git

black:  _venv_is_on
	black .
	black $(HIDDEN_PYTHON)

check:	_venv_is_on
	etc/git-hooks/pre-commit


all:	pkg docker doc

pkg:	_venv_is_on
	@mkdir -p dist
	python3 setup.py sdist --dist-dir dist

~/.pypirc:
	$(error You need to create $@ with an index-server section for "$(pypi)")

pypi:	~/.pypirc pkg
	twine upload -r "$(pypi)" "dist/docma-$(DOCMA_VERSION).tar.gz"

docker:	pkg
	$(DOCKER_BUILD) --rm --build-arg DOCMA_VERSION="$(DOCMA_VERSION)" \
		-t "docma:$(DOCMA_VERSION)" -t docma:latest .

doc spell:
	$(MAKE) -C doc $(MAKECMDGOALS) dist=$(abspath dist)

# This is redundant now. Use `docma new ...` instead
cookie:	dist/cookiecutter-docma-$(DOCMA_VERSION).zip

dist/cookiecutter-docma-$(DOCMA_VERSION).zip: _venv_is_on $(shell find $(COOKIE_DIR))
	@echo Generating $@ - THIS IS OBSOLETE
	@mkdir -p dist
	@( \
		zip -q -r - $(COOKIE_DIR) \
			--exclude \
				'*dist/*' \
				'*.pyc' \
				'*__pycache__/*' \
				'*.swp' \
				'*.zip' \
				'*.tar.*' \
				'*-info/*' \
				'*/.DS_Store' \
			> $@ ; \
	) || (echo Failed -- Removing $@ ; $(RM) $@)


# ------------------------------------------------------------------------------
#  Test targets

coverage:
	@mkdir -p dist/test
	pytest --cov=. --cov-report html:dist/test/htmlcov -n "$(PYTEST_WORKERS)"

test:
	pytest -v -s -n "$(PYTEST_WORKERS)"

start stop up down:
	$(MAKE) -C test $(MAKECMDGOALS)

clean:
	$(RM) -r dist
	docker system prune -f
	docker volume prune -f
	docker network prune -f

count:
	tokei .
