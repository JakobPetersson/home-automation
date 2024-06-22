
.PHONY: pull
pull:
	echo "Pulling"
	docker compose pull

.PHONY: build
build:
	echo "Building"
	docker compose build

.PHONY: start
start:
	echo "Starting"
	docker compose up -d --remove-orphans

.PHONY: stop
stop:
	echo "Stopping"
	docker compose stop

.PHONY: remove
remove: stop
	echo "Removing"
	docker compose rm -f

.PHONY: reset
reset: pull build remove start

.PHONY: logs
logs:
	echo "Logs"
	docker compose logs -f
