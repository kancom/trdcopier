.DEFAULT_GOAL := help

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'



test-unit: ## run unit tests
	pipenv run pytest -m "not integration" $(PYTEST_ARGS)

test-unit-verbose:
	$(MAKE) test-unit PYTEST_ARGS='-vv'

test: ## run all tests
	pipenv run pytest --cov-report term-missing --cov=src $(PYTEST_ARGS)

test-verbose:
	$(MAKE) test PYTEST_ARGS='-vv'

dev-run: ## run server app in DEGBU mode
	pipenv run python src/main.py

e2e-run: ## run server app in DEGBU mode
	pipenv run python src/e2e_main.py
