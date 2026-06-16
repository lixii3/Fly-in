# TODO: RIFAI TUTTO

PYTHON = python3
VENV = .venv
BIN = $(VENV)/bin

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
# 	$(BIN)/pip install flake8
# 	$(BIN)/pip install mypy
	$(BIN)/pip install poetry
	poetry install

run:
	$(BIN)/$(PYTHON) a_maze_ing.py config.txt

debug:
	$(BIN)/$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf $(VENV)
	rm -rf mazegen/__pycache__
	rm -rf output_maze.txt

lint:
	$(BIN)/flake8 a_maze_ing.py mazegen
	$(BIN)/mypy a_maze_ing.py mazegen --warn-return-any --warn-unused-ignores \
								   --ignore-missing-imports --disallow-untyped-defs \
								   --check-untyped-defs

lint-strict:
	flake8 a_maze_ing.py mazegen
	mypy a_maze_ing.py mazegen --strict

NUMBERS=0 1 2 3 4 5 6 7 8 9
test:
		$(foreach num, $(NUMBERS), $(BIN)/$(PYTHON) a_maze_ing.py configs/config$(num).txt;)


build:
	$(BIN)/pip install build
	$(BIN)/$(PYTHON) -m build --wheel

.PHONY: install run debug clean lint lint-strict build