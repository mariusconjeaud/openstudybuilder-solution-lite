ARG NGINX_IMAGE=nginx:alpine
ARG NODE_IMAGE=node:lts-alpine

## Build stage
FROM $NODE_IMAGE as build-stage

WORKDIR /app

## Install Node packages
COPY ./package*.json ./ ./
RUN yarn install

## Build the app
COPY ./ .
COPY ./config/config.json ./public/config.json
RUN yarn build

## Production stage
FROM $NGINX_IMAGE as prod-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./config/nginx/default.conf /etc/nginx/conf.d/default.conf

ARG PORT=5005
ENV PORT=$PORT
EXPOSE $PORT

## Runs healthcheck on the application root
## checks every `interval` seconds, fails if `timeout`,
## unhealthy status is reached if `retries` number of consecutive failures,
## but failures does not count within `start-period` seconds of start.
HEALTHCHECK --start-period=10s --timeout=2s --interval=10s --retries=2 CMD \
    curl --fail --silent --show-error --max-time 1 \
    "http://localhost:$PORT/" \
    > /dev/null || exit 1
