# ==============================================================
#							A_MAZE_ING
# ==============================================================

NAME = a_maze_ing.py
SRC = src

.DEFAULT_GOAL = install

.ONESHELL:
install:
	unzip -u mlx-2.2-py3-ubuntu-any.whl -d src
	rm -rf src/mlx-2.2.dist-info
	pip install flake8 mypy

run:
	python3 $(NAME) config.txt

debug:
	@echo "TODO"

lint:
	python3 -m flake8 .
	python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	python3 -m flake8 .
	python3 -m mypy . --strict

clean:

fclean: clean
	$(RM) -r src/mlx

re: fclean install

.PHONY: install run debug clean fclean re
