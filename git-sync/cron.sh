#!/usr/bin/env sh

set -eou > /dev/null

git_local_changes() {
  local CHANGED_FILES
  CHANGED_FILES=$( git status --porcelain | wc -l )
  [ "${CHANGED_FILES}" -gt 0 ]
}

if git_local_changes; then
  echo "There are local changes, skipping update."
  exit 0
fi

echo "There are no local changes"
