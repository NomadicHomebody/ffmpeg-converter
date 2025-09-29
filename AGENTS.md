# AGENTS.md – Build / Lint / Test commands and style guidelines

## Build
- Run the CLI with Python: `python mkv_mp4_bulk_converter.py <input_folder>`
- Python >=3.8 required; install deps with `pip install -r requirements.txt`

## Lint
- Run flake8 against project folder: `flake8 .`
- Run black for formatting: `black .`

## Test
- Run all tests: `pytest -q`
- Run a single test: `pytest -q <test_file>::<test_name>`
- Run with coverage: `pytest -q --cov=mkv_mp4_bulk_converter.py`

## Code Style
- Imports: absolute, standard libs first, third-party, local modules – sorted, no unused imports
- Formatting: 4-space indent, max line length 88, end-of-file newline
- Typing: use type hints (`list[str]`, `int`, etc.) and `my_type: type | None`
- Naming: snake_case for functions & variables, UpperCamelCase for classes, CONSTANTS in UPPER_SNAKE
- Error handling: explicit ValueError on bad inputs, use `try / except` for external calls, log via structlog, never swallow exceptions silently
- Logging: redact sensitive keys (`password`, `api_key`, `token`) using `redact_sensitive_fields`
- Documentation: docstrings per PEP 257, explain arguments, raises, returns; tests act as usage examples

## Testing Commands
- Run a specific test file: `pytest -q test_mkv_mp4_bulkConverter.py`
- Run a specific test: `pytest -q test_mkv_mp4_bulkConverter.py::test_conversion_complete`

## Environment
- Python >=3.8
- Virtual environment recommended: `python -m venv .venv` and `pip install -r requirements.txt`
- Use `pytest -q` to run tests quickly
- Run `flake8 . && black .` before pushing to ensure code quality and consistency
- Always ensure sensitive data is redacted in logs

## Rules
- No direct git commits; use `git add` and `git commit` with proper messages
- No test files are run without test coverage
- No code changes without proper type hints and documentation
- No untested code in pull requests
- No sensitive keys in logs; use `redact_sensitive_fields` for all logging

## Agent Guidelines
- Always check linting and formatting before committing
- Never commit without a test or test coverage
- Use `pytest -q <test_file>::<test_name>` to debug specific test issues
- Ensure all code changes follow the documented style rules
- Prefer `git add` and `git commit` for changes, not `git add .`
- Only commit when all linting and tests pass
- Always write docstrings and type hints for new code
- Redact sensitive information before logging
- Use `pytest` with `-q` for fast feedback and `--cov` for coverage

## Context7 MCP Tool Usage
- Use the `context7_get_library_docs` tool when researching any library documentation
- First resolve the library ID with `context7_resolve_library_id` before fetching docs
- Use `context7_get_library_docs` for: documentation queries, API examples, and code snippets
- Example: `context7_get_library_docs context7CompatibleLibraryID="..."`

## Pro Tip
Use `pytest -q` to test specific files or tests, e.g. `pytest -q test_mkv_mp4_bulkConverter.py::test_conversion_complete` to speed up debugging and development.