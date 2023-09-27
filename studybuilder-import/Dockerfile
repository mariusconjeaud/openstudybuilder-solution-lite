ARG PYTHON_IMAGE=python:3.11.3-slim

## In shared stage we create the environment and settings that are shared between prod and dev
FROM $PYTHON_IMAGE

## Install required system packages
RUN pip install --upgrade pip pipenv wheel \
    # clean-up
    && rm -rf ~/.cache

## Create and user non-root user
ARG UID=1000
ARG USER=appuser
RUN useradd --home-dir /home/$USER --user-group --create-home --uid $UID $USER
USER $USER

## Commands below run relative to this working directory
ARG WORKDIR=/app
WORKDIR $WORKDIR

## Copy Pipfiles into the working directory
COPY ./Pipfile* ./

## Create virtual environment and install required packages
RUN pipenv sync \
    # clean-up
    && rm -rf ~/.cache
