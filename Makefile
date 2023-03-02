install:
	poetry install
	poetry env info

format:
	poetry run isort .
	poetry run black .

test:
	poetry run pytest tests/

serve:
	poetry run uvicorn ticklist_mapper.api:app --reload --host 0.0.0.0

deploy:
	fly deploy

docker-build:
	docker build -t ticklistmapper .

docker-shell:
	docker run -it ticklistmapper /bin/bash

docker-run:
	docker run -p 8000:8000 ticklistmapper
