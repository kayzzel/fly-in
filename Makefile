#-------------------------------- VARIABLES ----------------------------------#

NAME		=	fly_in.py
MAP			?=	maps/easy/01_linear_path.txt

#-------------------------------- RULES --------------------------------------#

.PHONY: all install run debug clean fclean re reset lint test format check help

all: install run

install:
	poetry install

run:
	@poetry run python $(NAME) $(MAP)

debug:
	@poetry run python -m pdb $(NAME) $(MAP)

test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ -v --cov=. --cov-report=html
	@echo "Coverage report generated in htmlcov/"

format:
	poetry run black .
	poetry run isort .

lint:
	poetry run flake8 .
	poetry run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	poetry run flake8 .
	poetry run mypy . --strict


check: format lint

clean:
	find . -name "__pycache__" -type d -exec rm -rf "{}" +
	find . -name "*.pyc" -delete
	find . -name ".mypy_cache" -type d -exec rm -rf "{}" +
	find . -name ".pytest_cache" -type d -exec rm -rf "{}" +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf "{}" +

fclean: clean
	poetry env remove --all

re: fclean install

reset: fclean
	rm -f poetry.lock
	poetry install

help:
	@echo "Available rules:"
	@echo "  all        	- Install and run"
	@echo "  install    	- Install dependencies"
	@echo "  run        	- Run the project (MAP=... to override map)"
	@echo "  debug      	- Run with pdb debugger"
	@echo "  test       	- Run tests"
	@echo "  test-cov   	- Run tests with coverage report"
	@echo "  format     	- Format code with black and isort"
	@echo "  lint       	- Run flake8 and mypy"
	@echo "  lint-strict	- Run flake8 and mypy in strict mode"
	@echo "  check      	- Format then lint"
	@echo "  clean      	- Remove cache files"
	@echo "  fclean     	- clean + remove venv"
	@echo "  re         	- fclean + install"
	@echo "  reset      	- fclean + remove poetry.lock + install"
