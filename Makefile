.PHONY: lint test check

lint:
	ruff check .

test:
	pytest

check: lint test

