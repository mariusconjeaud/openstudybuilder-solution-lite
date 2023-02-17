FROM python:3.7.12-slim

ARG UID=1000
ARG USER=appuser
ARG WORKDIR=/app
ARG UVICORN_PORT="8000"
ARG UVICORN_HOST="0.0.0.0"
ARG UVICORN_ROOT_PATH=""

## Install system packages
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install git curl python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 \
    # required on ARM Mac
    && [ "x$(arch)" = "xx86_64" ] || apt-get install -y libgeos-dev \
    # clean-up
    && apt-get clean && rm -r /var/lib/apt/lists

# Install pipenv and upgrade setup tools system-wide
RUN pip install --upgrade pip pipenv wheel \
    # clean-up
    && rm -rf ~/.cache

## Create non-root user
RUN useradd --home-dir /home/$USER --user-group --create-home --uid $UID $USER

## Commands below run relative to this working directory
WORKDIR $WORKDIR

## Create virtual environment according to Pipfile.lock into user's home as root
COPY ./Pipfile* ./
RUN HOME=/home/$USER pipenv sync \
    # clean-up
    && rm -rf ~/.cache

## Copy the rest of the application owned by root
COPY . ./

## Byte-code compile application as root
RUN python -m compileall -f -j 0 $WORKDIR

## Run the rest as non-root user
USER $USER

## Open up a port to listen on
EXPOSE $UVICORN_PORT

## Environment variables, use sane defaults, then override them at instantiation
## Preferred to configure Uvicorn using env vars with UVICORN_ prefix
ENV UVICORN_PORT="$UVICORN_PORT" \
    UVICORN_HOST="$UVICORN_HOST" \
    UVICORN_ROOT_PATH="$UVICORN_ROOT_PATH"

## Run healthcheck on the API endpoint:
## checks every `interval` seconds, fails if `timeout`,
## unhealthy status is reached if `retries` number of consecutive failures,
## but failures does not count within `start-period` seconds of start.
HEALTHCHECK --start-period=60s --timeout=3s --interval=10s --retries=2 CMD \
    curl --fail --silent --show-error --max-time 2 \
    "http://localhost:$UVICORN_PORT/system/healthcheck" \
    > /dev/null || exit 1

CMD pipenv run uvicorn clinical_mdr_api.main:app
