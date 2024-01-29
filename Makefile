.PHONY: help
help: ## Help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
PROJECT_NAME := 'permission-manager:dev'

.PHONY: build
build: ## Build
	@docker build -t $(PROJECT_NAME) .

.PHONY: shell
shell: ## Shell
	@docker run --rm -it -v "$(CURDIR):/code" $(PROJECT_NAME) /bin/bash

.PHONY: test
test: ## Test
	@docker run --rm -it -v "$(CURDIR):/code" $(PROJECT_NAME) /bin/bash -c pytest $(c)

.PHONY: linters
linters: ## Run linters
	@docker run --rm -it -v "$(CURDIR):/code" $(PROJECT_NAME) /bin/bash -c 'ruff format .; ruff check . --fix'
