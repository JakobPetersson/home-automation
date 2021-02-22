#!/usr/bin/env sh

set -eou > /dev/null

setup_usb_access_rights() {
  if groups | grep dialout > /dev/null; then
    echo "User ${USER} already member of dialout group"
    return
  fi

  if ! which gpasswd > /dev/null; then
    >&2 echo "Error: gpasswd not found"
  fi

  # Add user to dialout group
  sudo gpasswd --add "${USER}" dialout
}

setup_docker() {
  if which docker > /dev/null; then
    echo "Docker already installed"
    return
  fi

  echo "Installing docker"
  sudo snap install docker
}


setup_usb_access_rights
setup_docker
