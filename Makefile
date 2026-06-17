.PHONY: install run test test-py test-cpp build lint format check

install:
	uv sync

run:
	uv run fastapi dev

test-py:
	uv run pytest

test-cpp: build
	./build/run_tests

test: test-cpp test-py

build:
	mkdir -p build/ && cmake -S . -B ./build && cd ./build && make

lint:
	uv run ruff check --fix

format:
	uv run ruff format

check: format lint test
