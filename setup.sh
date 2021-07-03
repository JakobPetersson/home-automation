#!/usr/bin/env sh
#
# Script to setup requirements:
# - Install Docker (and group access to docker commands)
# - Setup usb serial access rights
#

set -eou > /dev/null

setup_usb_serial_access_rights() {
  if groups | grep dialout > /dev/null; then
    echo "User ${USER} already member of dialout group"
    return
  fi

  if ! which gpasswd > /dev/null; then
    >&2 echo "Error: gpasswd not found"
  fi

  # Add user to dialout group
  sudo gpasswd --add "${USER}" dialout

  # Activate changes to group
  newgrp dialout
}

setup_docker() {
  if which docker > /dev/null; then
    echo "Docker already installed"
    return
  fi

  echo "Installing docker"
  sudo snap install docker
}

setup_docker_group() {
  if groups | grep docker > /dev/null; then
    echo "User ${USER} already member of docker group"
    return
  fi

  # Create docker group if it does not exist
  sudo groupadd --force docker

  if ! which gpasswd > /dev/null; then
    >&2 echo "Error: gpasswd not found"
  fi

  # Add user to group group
  sudo gpasswd --add "${USER}" docker

  # Activate changes to group
  newgrp docker

  # Try docker command
  if ! docker --help; then
    >&2 echo "Error: Failed to execute docker --help command to test that docker is working"
  fi
}

setup_usb_serial_access_rights
setup_docker
setup_docker_group
