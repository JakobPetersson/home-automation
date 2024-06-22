#!/usr/bin/env sh

set -eou > /dev/null

THIS_DIR=$(cd "$(dirname "$0")"; pwd -P)

readonly LOCAL_BRANCH=main
readonly REMOTE_BRANCH=origin/main

#
# Check if there are local changes in repo
#
git_local_changes() {
  local CHANGED_FILES
  CHANGED_FILES=$( git status --porcelain | wc -l )
  [ "${CHANGED_FILES}" -gt 0 ]
}

#
# Write to git sync log-file
#
git_sync_log() {
  echo "$(date --iso-8601=seconds) | ${1}" >> "${THIS_DIR}/git-sync.log"
}

#
#
#
git_sync() {
  local _REPO_DIR="${1}"

  (
    # cd into repo
    cd "${_REPO_DIR}"

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

    git_sync_log "Updating containers"
    make start

    git_sync_log "Containers restarted"
  )
}

git_sync "${THIS_DIR}"
