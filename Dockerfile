FROM python:3.10

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./ticklist_mapper /src/ticklist_mapper
COPY ./static /src/static
COPY ./pyproject.toml /src/pyproject.toml
COPY ./poetry.lock /src/poetry.lock

RUN pip install .

# CMD ["uvicorn", "ticklist_mapper.api:app", "--host", "0.0.0.0", "--port", "8080"]
CMD ["uvicorn", "ticklist_mapper.api:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
