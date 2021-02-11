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

git_branches_differ() {
  local BRANCH_A="${1}"
  local BRANCH_B="${2}"

  git diff --exit-code "${BRANCH_A}" "${BRANCH_B}" > /dev/null
}

git_sync() {
  if git_local_changes; then
    echo "There are local changes, skipping sync"
    exit 0
  fi

  echo "There are no local changes"

  git_fetch

  if git_branches_differ "${LOCAL_BRANCH}" "${REMOTE_BRANCH}"; then
    echo "Local branch equals remote branch"
    exit 0
  fi

  echo "Local branch differs from remote"

}

git_sync
