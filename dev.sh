#!/usr/bin/env bash

set -eou > /dev/null

COMPOSE_PATH="$( cd "$(dirname "$0")" ; pwd -P )/docker-compose.yml"

pull() {
  echo "Pulling"
  docker-compose -f "$COMPOSE_PATH" pull
}

build() {
  echo "Building"
  docker-compose -f "$COMPOSE_PATH" build
}

start() {
  echo "Starting"
  docker-compose -f "$COMPOSE_PATH" up -d --remove-orphans
}

stop() {
  echo "Stopping"
  docker-compose -f "$COMPOSE_PATH" stop
}

remove() {
  stop
  echo "Removing"
  docker-compose -f "$COMPOSE_PATH" rm -f
}

reset() {
  pull
  build
  remove
  start
}

logs() {
  echo "Logs"
  docker-compose -f "$COMPOSE_PATH" logs -f
}

for ARG in "$@"; do
  case "${ARG}" in
    pull)
      pull;;
    build)
      build;;
    start)
      start;;
    stop)
      stop;;
    reset)
      reset;;
    remove)
      remove;;
    logs)
      logs;;
    *)
      echo "Unknown command: ${ARG}"
      exit 1
      ;;
  esac
done
