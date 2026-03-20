#-------------------------------- VARIABLES ----------------------------------#
NAME		=	fly_in.py
MAP			?=	maps/easy/01_linear_path.txt
VENV		=	.venv

#-------------------------------- RULES --------------------------------------#


all: install run


install:
	poetry install


run:
	@poetry run python $(NAME) $(MAP)


debug:
	@poetry run python -m pdb $(NAME) $(CONFIG_FILE)


clean:
	find . -name "__pycache__" -type d -exec rm -rf "{}" +
	find . -name "*.pyc" -delete
	find . -name ".mypy_cache" -type d -exec rm -rf "{}" +
	find . -name ".pytest_cache" -type d -exec rm -rf "{}" +
	find . -name ".coverage" -delete

fclean: clean
	rm -rf $(VENV)
	poetry env remove --all


lint:
	poetry run flake8 . --exclude $(VENV)
	poetry run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV)


.PHONY: all install run debug clean lint
