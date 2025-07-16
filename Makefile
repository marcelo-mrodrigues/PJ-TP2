.PHONY: install test lint format coverage clean run-dev

install:
	@echo "Backend (Python)"
	python3 -m venv backend/venv
	./backend/venv/bin/pip install -r backend/requirements.txt
	@echo "\n- Frontend (Node.js)"
	npm --prefix ./frontend install ./frontend
	@echo "\n hooks de pre-commit..."
	./backend/venv/bin/pre-commit install
	@echo "\n ambiente pronto"

test:
	@echo "\n rodando testes do Backend"
	./backend/venv/bin/pytest backend/
	@echo "\n rodando testes do Frontend"
	npm --prefix ./frontend test

# linters
lint:
	@echo "\n Rodando linters do Backend (flake8)..."
	./backend/venv/bin/flake8 backend/
	@echo "\n Rodando linters do Frontend (eslint)..."
	npm --prefix ./frontend run lint

# Formata
format:
	@echo " Formatando código do Backend (black)..."
	./backend/venv/bin/black backend/
	@echo "\n Formatando código do Frontend (prettier)..."
	npm --prefix ./frontend run format

# cobertura (pode mudar ainda)
coverage:
	@echo "--- Gerando relatório de cobertura do Backend..."
	./backend/venv/bin/coverage run -m pytest backend/
	./backend/venv/bin/coverage report -m
	@echo "\n--- Gerando relatório de cobertura do Frontend..."
	npm --prefix ./frontend test -- --coverage

# roda front
run-dev:
	npm --prefix ./frontend run dev

# Inicia o servidor de desenvolvimento do Backend (Django)
run-backend:
	@echo "--- Iniciando servidor de desenvolvimento Backend (Django)..."
	./backend/venv/bin/python backend/manage.py runserver

# cache e build limpados
clean:
	@echo "--- Limpando arquivos de cache..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf frontend/.next
	rm -f backend/.coverage