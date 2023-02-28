install:
	poetry install
	poetry env info

serve:
	poetry run uvicorn ticklist_mapper.api:app --reload

deploy:
	flyctl deploy

docker-build:
	docker build -t ticklistmapper .

docker-shell:
	docker run -it ticklistmapper /bin/bash

docker-run:
	docker run -p 8000:8000 ticklistmapper
