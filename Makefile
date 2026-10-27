.PHONY: install run test lint format smoke docker-up docker-down

install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	python -m app.main

test:
	pytest

lint:
	ruff check app tests smoke_test.py

format:
	ruff format app tests smoke_test.py

smoke:
	python smoke_test.py

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
