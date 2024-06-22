# home-automation

Configuration and setup for my Home Automation project.

I currently have this running on a Raspberry PI 4 (8GB).

## Setup

Checkout this repository and run `setup.sh` to install docker and configure usb access rights.

```sh
./setup.sh
```

### git sync

`git-sync.sh` is a small script for syncing code updates from git.

#### Setup

Run `git-sync.sh` on a timer to pull changes from repo.

Edit cron settings

```sh
crontab -e
```

and add:

```sh
*/1 * * * * PATH=$PATH::/snap/bin <ABSOLUTE_PATH_TO_REPO>/git-sync.sh >> /dev/null 2>&1
```
