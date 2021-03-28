.DEFAULT_GOAL := help
SHELL = bash

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

########################################################################
# first step for local dev
########################################################################
install-dev: ## install base and dev dependencies
	pipenv install --dev
	pipenv install -e .

########################################################################
# code quality
########################################################################

########################################################################
# testing local
########################################################################

test-unit: ## run unit tests
	pipenv run pytest -m "not integration" $(PYTEST_ARGS)

test-unit-verbose:
	$(MAKE) test-unit PYTEST_ARGS='-vv'

test: ## run all tests
	pipenv run pytest --cov-report term-missing --cov=src $(PYTEST_ARGS)

test-verbose:
	$(MAKE) test PYTEST_ARGS='-vv'

dev-run: ## run server app in DEBUG mode
	pipenv run python src/main.py


########################################################################
# building docker images
########################################################################
build-restapi: ## docker build rest api
	docker-compose -f docker-compose.yml build restapi

build-router: ## docker build router
	docker-compose -f docker-compose.yml build router
########################################################################
# bringing apps in docker
########################################################################
down: ## stop and down all the containers
	docker-compose down

status: ## status for all dockers
	docker-compose -f docker-compose.yml ps

up-restapi: build-restapi ## docker build & run rest api
	docker-compose -f docker-compose.yml up -d restapi

up-router: build-router ## docker build & run router
	docker-compose -f docker-compose.yml up -d router

up-gitlab: ## bring up gilab
	docker-compose -f docker-compose.yml up -d gitlab
