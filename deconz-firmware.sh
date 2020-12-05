#!/usr/bin/env sh

docker run \
  --rm \
  -it \
  --entrypoint "/firmware-update.sh" \
  --privileged \
  --cap-add=ALL \
  -v /dev:/dev \
  -v /lib/modules:/lib/modules \
  -v /sys:/sys \
  marthoc/deconz
