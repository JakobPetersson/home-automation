#!/usr/bin/env sh

set -eou > /dev/null

readonly LOCAL_BRANCH=main
readonly REMOTE_BRANCH=origin/main

git_local_changes() {
  local CHANGED_FILES
  CHANGED_FILES=$( git status --porcelain | wc -l )
  [ "${CHANGED_FILES}" -gt 0 ]
}

git_fetch() {
  git fetch
}

git_sync() {
  if git_local_changes; then
    echo "There are local changes, skipping update."
    exit 0
  fi

  echo "There are no local changes"

  git_fetch
}

git_sync
