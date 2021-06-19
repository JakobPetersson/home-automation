#!/usr/bin/env sh

set -eou > /dev/null

THIS_DIR=$(cd "$(dirname "$0")"; pwd -P)

APPDAEMON_GIT_DIR="${THIS_DIR}/appdaemon-git"

APPDAEMON_VERSION=4.0.8

if [ ! -d "${APPDAEMON_GIT_DIR}" ]; then
  git clone https://github.com/AppDaemon/appdaemon.git "${APPDAEMON_GIT_DIR}"
fi

if [ ! -d "${APPDAEMON_GIT_DIR}" ]; then
  echo "Error cloning Appdaemon"
fi

cd "${APPDAEMON_GIT_DIR}"

git fetch --all

echo "Checking out ${APPDAEMON_VERSION}"

git checkout "${APPDAEMON_VERSION}"
