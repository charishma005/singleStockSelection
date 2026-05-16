test:
	pytest tests/test_app.py

lint:
	black .
	isort .
	flake8 .
	mypy .

build:
	docker build -t fastapi-app .

run:
	docker run -p 8000:8000 fastapi-app