
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


.PHONY: black help _venv_is_off _venv_is_on _venv update check doc spell test coverage

DOCMA_VERSION=$(shell cat docma/VERSION)
DOCMA_URL=https://github.com/jin-gizmo/docma
DOCMA_SOURCE=https://github.com/jin-gizmo/docma.git
DOCMA_DOC=https://jin-gizmo.github.io/docma

# .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
# Docker settings
platform=linux/amd64,linux/arm64
# This is the jindr default
registry=localhost:5001
# Add --progress=plain for debugging
DOCKER_BUILD=docker buildx build --platform="$(platform)"
BUILD_DATE=$(shell date -u +%Y-%m-%dT%H:%M:%SZ)
ifneq ($(registry),)
REGISTRY=$(registry:%/=%)/
endif

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
	@echo "   docker:    Build a docker image with docma installed. Add registry=..."
	@echo "              to specify the target registry. Use \"registry=\" to push to"
	@echo "              Docker Hub. Defaults to \"$(registry)\" provided by jindr."
	@echo "   pkg:       Build the Python package."
	@echo "   pypi:      Upload the pkg to the \"$(pypi)\" PyPI server via twine. The"
	@echo "              \"$(pypi)\" server must be defined in ~/.pypirc. Add pypi=..."
	@echo "              to specify a different index server entry in ~/.pypirc."
	@echo
	@echo "[31mUser guide / documentation targets[0m"
	@echo "   doc:       Make the user guide into consolidated markdown."
	@echo "   preview:   Build and preview the mkdocs version of the user guide."
	@echo "   publish:   Publish the user guide to GitHub pages (must be on master branch)."
	@echo "   spell:     Spell check the user guide (requires aspell)."
	@echo
	@echo "[31mMiscellaneous targets[0m"
	@echo "   black      Format the code using black."
	@echo "   check:     Run some code checks (flake8 etc)."
	@echo "   clean:     Remove generated components, fluff etc."
	@echo "   count:     Do line counts on source code (needs tokei)."
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
	etc/git-hooks/pre-commit --manual


all:	pkg docker doc

pkg:	_venv_is_on
	@mkdir -p dist
	python3 setup.py sdist --dist-dir dist

~/.pypirc:
	$(error You need to create $@ with an index-server section for "$(pypi)")

pypi:	~/.pypirc pkg
	twine upload -r "$(pypi)" "dist/docma-$(DOCMA_VERSION).tar.gz"

docker:	pkg
	( \
		[[ "$(registry)" == localhost:* ]] && jindr --registry "$(registry)" up ; \
		set -e ; \
		TMP=$$(mktemp -d) ; \
		z=1 ; \
		trap '/bin/rm -rf $$TMP; exit $$z' 0 ; \
		cp Dockerfile "dist/docma-$(DOCMA_VERSION).tar.gz" $$TMP ; \
		$(DOCKER_BUILD) --rm --push --pull \
			-t "$(REGISTRY)docma:$(DOCMA_VERSION)"  \
			-t "$(REGISTRY)docma:latest" \
			--build-arg DOCMA_VERSION="$(DOCMA_VERSION)" \
			--label org.opencontainers.image.created="$(BUILD_DATE)" \
			--label org.opencontainers.image.version="$(DOCMA_VERSION)" \
			$$TMP ; \
		z=0 ; \
	)

# ------------------------------------------------------------------------------
# Documentation related targets
doc spell preview publish:
	$(MAKE) -C doc $(MAKECMDGOALS) dist=$(abspath dist)


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
