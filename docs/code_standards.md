# Code Standards and Documentation Format

## 1. Code Style
- Follow **PEP 8** compliance for all Python code.
- Maximum line length should be 88 characters (Black formatter standard).
- Use clear, descriptive variable and function names.

## 2. Documentation
- All functions and classes must include **Docstrings** using the Google format.
- Code should be self-documenting as much as possible, with inline comments used only to explain *why* something is done, not *what* is done.

## 3. Type Hinting
- Utilize Python type hints (`typing` module) for function arguments and return types to improve code readability and enable static analysis.

## 4. Testing
- Write tests for all logic using `pytest`.
- Maintain test coverage above 80%.
- Name test files with a `test_` prefix (e.g., `test_parser.py`).

## 5. Logging
- Use the centralized logger in `utils.logger` rather than basic `print()` statements.
- Ensure appropriate log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) are used logically.
