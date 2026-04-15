.PHONY: install dev lint test clean help

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias y CLI
	pip install -e .

dev: ## Instalar con dependencias de desarrollo
	pip install -e ".[dev]"

lint: ## Ejecutar ruff (linter + formatter)
	ruff check cli/
	ruff format --check cli/

format: ## Formatear código automáticamente
	ruff format cli/
	ruff check --fix cli/

test: ## Ejecutar tests
	pytest tests/ -v

clean: ## Limpiar cachés y builds
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf dist/ build/ .pytest_cache/ .ruff_cache/

setup: ## Setup inicial completo (primera vez)
	@echo "→ Instalando dependencias..."
	@make install
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "→ Fichero .env creado. Añade tu OPENAI_API_KEY."; \
	else \
		echo "→ .env ya existe."; \
	fi
	@echo ""
	@echo "✓ Listo. Siguiente paso:"
	@echo "  1. Edita .env y añade tu OPENAI_API_KEY"
	@echo "  2. Ejecuta: bbcopilot vault-list"
	@echo "  3. Ejecuta: bbcopilot ask 'tu primera pregunta'"

vault: ## Listar playbooks del vault
	bbcopilot vault-list

ask: ## Ejemplo rápido de uso (make ask Q="tu pregunta")
	bbcopilot ask "$(Q)"
