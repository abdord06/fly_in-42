PYTHON = python3
UV = uv
MAP ?= 01_easy.txt

.PHONY: install run debug clean lint lint-strict

install:
	$(UV) pip install -r requirements.txt

run:
	$(PYTHON) main.py $(MAP)

debug:
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
	rm -rf src/__pycache__
	rm -rf llm_sdk/__pycache__

lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 .
	mypy --strict .