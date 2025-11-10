.PHONY: help install-all test lint format


help: ## Mostrar esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install-all: ## Install all dependency groups (production + dev)
	@echo "📦 Installing all dependencies (production + dev)..."
	uv sync --all-groups
	@echo "✅ All dependencies installed successfully!"

test: ## Run tests
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v

lint: ## Lint code
	uv run ruff check . --fix

format: ## Format code
	uv run ruff format .

start-api: ## start api server
	uv run python src/template-api/api.py --host 0.0.0.0 --port 8000 --reload --log-level debug
