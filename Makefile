# TODO: RIFAI TUTTO
NAME = main.py
PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install flake8 mypy poetry
	$(BIN)/poetry install

run:
	$(BIN)/$(PYTHON) $(NAME)

debug:
	$(BIN)/$(PYTHON) -m pdb $(NAME)

clean:
	rm -rf $(VENV)
	rm -rf fly_in/__pycache__

lint:
	$(BIN)/flake8 $(NAME) fly_in
	$(BIN)/mypy $(NAME) fly_in --warn-return-any --warn-unused-ignores \
								--ignore-missing-imports --disallow-untyped-defs \
								--check-untyped-defs

lint-strict:
	$(BIN)/flake8 $(NAME) fly_in
	$(BIN)/mypy $(NAME) fly_in --strict

build:
	poetry build -f wheel

.PHONY: install run debug clean lint lint-strict build