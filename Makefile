.PHONY: install run test test-py test-cpp build lint format check clear
.PHONY: run-cpp analyze-benchmark-py analyze-benchmark-cpp

install:
	uv sync

run:
	NUM_WORKERS=$(or $(WORKERS),4) uv run uvicorn server.app:app --host 0.0.0.0 --port 8000

run-client:
	uv run client

run-cpp: build
	./build/dis 8000 $(or $(WORKERS),4)

test-py:
	uv run pytest

test-cpp: build
	./build/run_tests

test: test-cpp test-py

build:
	mkdir -p build/ && cmake -S . -B ./build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && cd ./build && make

lint:
	uv run ruff check --fix

format:
	uv run ruff format

clear:
	rm imagens/*.png
	rm -f reconstruction_report.csv

check: format lint test

analyze-benchmark-py:
	uv run python analyze_benchmark.py workers_results/python python

analyze-benchmark-cpp:
	uv run python analyze_benchmark.py workers_results/cpp cpp
