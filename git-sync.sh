#!/usr/bin/env sh

set -eou > /dev/null

THIS_DIR=$(cd "$(dirname "$0")"; pwd -P)

cd "${THIS_DIR}"

readonly LOCAL_BRANCH=main
readonly REMOTE_BRANCH=origin/main

git_local_changes() {
  local CHANGED_FILES
  CHANGED_FILES=$( git status --porcelain | wc -l )
  [ "${CHANGED_FILES}" -gt 0 ]
}

git_sync_log() {
  echo "$(date --iso-8601=seconds) | ${1}" >> "${THIS_DIR}/git-sync.log"
}

git_sync() {
  if git_local_changes; then
    echo "There are local changes, skipping sync"
    exit 0
  fi

  echo "There are no local changes"

  echo "Fetching"
  git fetch

  if git diff --exit-code "${LOCAL_BRANCH}" "${REMOTE_BRANCH}" > /dev/null; then
    echo "Local branch equals remote branch"
    exit 0
  fi

  echo "Local branch differs from remote"

  echo "Pulling"
  git pull
  
  git_sync_log "Updated from git"

  echo "Updating containers"
  ./dev.sh start
}

git_sync
