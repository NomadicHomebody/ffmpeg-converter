# AGENTS.md – Build / Lint / Test commands and style guidelines

## Build
- Run the CLI with Python: `python mkv_mp4_bulk_converter.py <input_folder>`
- Python >=3.8 required; install deps with `pip install -r requirements.txt`

## Lint
- Optional: Install linter `pip install flake8 black`
- Run flake8 against project folder: `flake8 .`
- Run black for formatting: `black .`

## Test
- Run all tests: `pytest -q`
- Run a single test: `pytest -q <test_file>::<test_name>`

## Code Style
- Imports: absolute, standard libs first, third-party, local modules – sorted, no unused imports.
- Formatting: 4-space indent, max line length 88, end-of-file newline.
- Typing: use type hints (`list[str]`, `int`, etc.) and `my_type: type | None`.
- Naming: snake_case for functions & variables, UpperCamelCase for classes, CONSTANTS in UPPER_SNAKE.
- Error handling: explicit ValueError on bad inputs, use `try / except` for external calls, log via structlog, never swallow exceptions silently.
- Logging: redact sensitive keys (`password`, `api_key`, `token`) using `redact_sensitive_fields`.
- Documentation: docstrings per PEP 257, explain arguments, raises, returns; tests act as usage examples.