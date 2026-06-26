.PHONY: install run test test-py test-cpp build lint format check

install:
	uv sync

run:
	uv run fastapi dev

run-client:
	uv run client

run-cpp-server: build
	./build/dis

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

check: format lint test

benchmark:
	@mkdir -p benchmark_results
	@NUM_WORKERS=$(WORKERS) REPORT_FILE=benchmark_results/report_$(WORKERS)w.csv make run

analyze-benchmark:
	uv run python3 analyze_benchmark.py benchmark_results/
