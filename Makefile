.PHONY : all

test:
	poetry run pytest

black:
	poetry run black .

lint:
	poetry run black .
	poetry run isort .
	poetry run flake8

all: lint test
