FROM python:3.8-slim  AS base

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && apt install -y curl

RUN pip install pipenv

WORKDIR /app
COPY ./Pipfile /app
COPY ./Pipfile.lock /app

RUN pipenv install

FROM base AS pkts

COPY ./ /app
