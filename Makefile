UV = uv
PYTHON = $(UV) run python
MAP ?= 01_easy.txt

.PHONY: install run debug clean lint lint-strict


install:
	$(UV) sync

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf src/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint:
	$(UV) run flake8 .
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV) run flake8 .
	$(UV) run mypy . --strict