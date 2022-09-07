FROM python:3.10-slim-buster

RUN apt update && apt install --no-install-recommends -y gcc libc6-dev libpq-dev && rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN pip install poetry==1.1.5

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY /scripts /app/scripts/
COPY README.md /app/README.md

RUN poetry install --no-dev

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app/

CMD poetry run prod
