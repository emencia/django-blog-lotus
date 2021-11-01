PYTHON_INTERPRETER=python3
VENV_PATH=.venv

PYTHON_BIN=$(VENV_PATH)/bin/python
PIP=$(VENV_PATH)/bin/pip
DJANGO_MANAGE=$(VENV_PATH)/bin/python sandbox/manage.py
FLAKE=$(VENV_PATH)/bin/flake8
PYTEST=$(VENV_PATH)/bin/pytest
TWINE=$(VENV_PATH)/bin/twine
TOX=$(VENV_PATH)/bin/tox
SPHINX_RELOAD=$(VENV_PATH)/bin/python sphinx_reload.py

DEMO_DJANGO_SECRET_KEY=samplesecretfordev
PACKAGE_NAME=django-blog-lotus
PACKAGE_SLUG=`echo $(PACKAGE_NAME) | tr '-' '_'`
APPLICATION_NAME=lotus

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo
	@echo "  install             -- to install this project with virtualenv and Pip"
	@echo "  freeze-dependencies -- to write a frozen.txt file with installed dependencies versions"
	@echo
	@echo "  clean               -- to clean EVERYTHING (Warning)"
	@echo "  clean-var           -- to clean data (uploaded medias, database, etc..)"
	@echo "  clean-doc           -- to remove documentation builds"
	@echo "  clean-install       -- to clean Python side installation"
	@echo "  clean-pycache       -- to remove all __pycache__, this is recursive from current directory"
	@echo
	@echo "  run                 -- to run Django development server"
	@echo "  migrate             -- to apply demo database migrations"
	@echo "  migrations          -- to create new migrations for application after changes"
	@echo "  superuser           -- to create a superuser for Django admin"
	@echo "  demo                -- to fill database with demo datas (this removes every existing Author, Article and Category objects)"
	@echo
	@echo "  css                 -- to build uncompressed CSS from Sass sources"
	@echo "  watch-css           -- to watch for Sass changes to rebuild CSS"
	@echo "  css-prod            -- to build compressed and minified CSS from Sass sources"
	@echo
	@echo "  docs                -- to build documentation"
	@echo "  livedocs            -- to run livereload server to rebuild documentation on source changes"
	@echo
	@echo "  flake               -- to launch Flake8 checking"
	@echo "  test                -- to launch base test suite using Pytest"
	@echo "  test-initial        -- to launch tests with pytest and re-initialized database (for after new application or model changes)"
	@echo "  tox                 -- to launch tests for every Tox environments"
	@echo "  quality             -- to launch Flake8 checking and every tests suites"
	@echo
	@echo "  check-release	     -- to check package release before uploading it to PyPi"
	@echo "  release             -- to release package for latest version on PyPi (once release has been pushed to repository)"
	@echo

clean-pycache:
	@echo ""
	@echo "==== Clear Python cache ===="
	@echo ""
	rm -Rf .pytest_cache
	find . -type d -name "__pycache__"|xargs rm -Rf
	find . -name "*\.pyc"|xargs rm -f
.PHONY: clean-pycache

clean-install:
	@echo ""
	@echo "==== Clear installation ===="
	@echo ""
	rm -Rf $(VENV_PATH)
	rm -Rf $(PACKAGE_SLUG).egg-info
.PHONY: clean-install

clean-var:
	@echo ""
	@echo "==== Clear var/ directory ===="
	@echo ""
	rm -Rf var
.PHONY: clean-var

clean-doc:
	@echo ""
	@echo "==== Clear documentation ===="
	@echo ""
	rm -Rf docs/_build
.PHONY: clean-doc

clean: clean-var clean-doc clean-install clean-pycache
.PHONY: clean

venv:
	@echo ""
	@echo "==== Install virtual environment ===="
	@echo ""
	virtualenv -p $(PYTHON_INTERPRETER) $(VENV_PATH)
	# This is required for those ones using old distribution
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade setuptools
.PHONY: venv

create-var-dirs:
	@mkdir -p var/db
	@mkdir -p var/static/css
	@mkdir -p var/media
	@mkdir -p sandbox/media
	@mkdir -p sandbox/static/css
.PHONY: create-var-dirs

install: venv create-var-dirs
	@echo ""
	@echo "==== Install everything for development ===="
	@echo ""
	$(PIP) install -e .[breadcrumbs,dev]
	${MAKE} migrate
	npm install
.PHONY: install

migrations:
	@echo ""
	@echo "==== Making application migrations ===="
	@echo ""
	@DJANGO_SECRET_KEY=$(DEMO_DJANGO_SECRET_KEY) \
	$(DJANGO_MANAGE) makemigrations $(APPLICATION_NAME)
.PHONY: migrations

migrate:
	@echo ""
	@echo "==== Apply pending migrations ===="
	@echo ""
	@DJANGO_SECRET_KEY=$(DEMO_DJANGO_SECRET_KEY) \
	$(DJANGO_MANAGE) migrate
.PHONY: migrate

superuser:
	@echo ""
	@echo "==== Create new superuser ===="
	@echo ""
	@DJANGO_SECRET_KEY=$(DEMO_DJANGO_SECRET_KEY) \
	$(DJANGO_MANAGE) createsuperuser
.PHONY: superuser

demo:
	@echo ""
	@echo "==== Filling with demo datas ===="
	@echo ""
	@DJANGO_SECRET_KEY=$(DEMO_DJANGO_SECRET_KEY) \
	$(DJANGO_MANAGE) lotus_demo --flush-all --translation=fr --translation=de
.PHONY: demo

run:
	@echo ""
	@echo "==== Running development server ===="
	@echo ""
	@DJANGO_SECRET_KEY=$(DEMO_DJANGO_SECRET_KEY) \
	$(DJANGO_MANAGE) runserver 0.0.0.0:8001
.PHONY: run

css:
	@echo ""
	@echo "==== Build CSS ===="
	@echo ""
	npm run-script css
.PHONY: css

watch-sass:
	@echo ""
	@echo "==== Watching Sass sources ===="
	@echo ""
	npm run-script watch-css
.PHONY: watch-sass

css-prod:
	npm run-script css-prod
.PHONY: css-prod

docs:
	@echo ""
	@echo "==== Build documentation ===="
	@echo ""
	cd docs && make html
.PHONY: docs

livedocs:
	@echo ""
	@echo "==== Watching documentation sources ===="
	@echo ""
	$(SPHINX_RELOAD)
.PHONY: livedocs

flake:
	@echo ""
	@echo "==== Flake ===="
	@echo ""
	$(FLAKE) --statistics --show-source $(APPLICATION_NAME)
	$(FLAKE) --statistics --show-source tests
.PHONY: flake

test:
	@echo ""
	@echo "==== Tests ===="
	@echo ""
	$(PYTEST) -vv --reuse-db tests/
	rm -Rf var/media-tests/
.PHONY: test

test-initial:
	@echo ""
	@echo "==== Tests from zero ===="
	@echo ""
	$(PYTEST) -vv --reuse-db --create-db tests/
	rm -Rf var/media-tests/
.PHONY: test-initial

tox:
	@echo ""
	@echo "==== Launch all Tox environments ===="
	@echo ""
	$(TOX)
.PHONY: tox

freeze-dependencies:
	@echo ""
	@echo "==== Freeze dependencies versions ===="
	@echo ""
	$(VENV_PATH)/bin/python freezer.py
.PHONY: freeze-dependencies

build-package:
	@echo ""
	@echo "==== Build package ===="
	@echo ""
	rm -Rf dist
	$(VENV_PATH)/bin/python setup.py sdist
.PHONY: build-package

release: build-package
	@echo ""
	@echo "==== Release ===="
	@echo ""
	$(TWINE) upload dist/*
.PHONY: release

check-release: build-package
	@echo ""
	@echo "==== Check package ===="
	@echo ""
	$(TWINE) check dist/*
.PHONY: check-release


quality: test-initial flake docs check-release freeze-dependencies
	@echo ""
	@echo "♥ ♥ Everything should be fine ♥ ♥"
	@echo ""
.PHONY: quality
