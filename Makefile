.PHONY: install run test lint format typecheck check

install:
	uv sync

run:
	uv run fastapi dev

test:
	uv run pytest

lint:
	uv run ruff check --fix

format:
	uv run ruff format

check: format lint test
