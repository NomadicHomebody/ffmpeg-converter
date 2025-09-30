# AGENTS.md – Agent Workflow, Build, Lint, Test, and Style Guide

## Build & Environment
- Python 3.8+ required; install deps: `pip install -r requirements.txt`
- Run CLI: `python mkv_mp4_bulk_converter.py <input_folder>`
- Use virtualenv: `python -m venv .venv`

## Lint & Format
- Lint: `flake8 .`
- Format: `black .`

## Test
- Run all: `pytest -q`
- Run file: `pytest -q test/test_mkv_mp4_bulkConverter.py`
- Run single test: `pytest -q test/test_mkv_mp4_bulkConverter.py::test_conversion_complete`
- Coverage: `pytest -q --cov=mkv_mp4_bulk_converter.py`

## Code Style
- Imports: absolute, stdlib first, then third-party, then local; sorted, no unused
- Formatting: 4-space indent, max line 88, EOF newline
- Typing: use type hints everywhere (`list[str]`, `int`, etc.)
- Naming: snake_case (funcs/vars), UpperCamelCase (classes), UPPER_SNAKE (constants)
- Error handling: raise ValueError for bad input, use try/except for external calls, log via structlog, never swallow exceptions
- Logging: redact sensitive keys (`password`, `api_key`, `token`) using `redact_sensitive_fields`
- Docstrings: PEP 257, explain args/raises/returns; tests act as usage examples

## Agent Rules
- Always lint & format before commit
- Never commit untested code; always add/maintain tests
- Use `pytest -q <file>::<test>` to debug
- Only commit when all linting and tests pass
- Redact sensitive info in logs

## Library Docs
- Use `context7_get_library_docs` for up-to-date docs; resolve ID first
