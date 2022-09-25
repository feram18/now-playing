#!/usr/bin/bash
# Description: Update Now-Playing software (github.com/feram18/now-playing)

function clean() {
  rm -f "*.log*"
  sudo rm -rf "*/__pycache__"
  sudo rm -rf "__pycache__"
}

function updateRepository() {
  printf "Updating repository...\n"
  git reset --hard
  git fetch --tags
  tag="$(git describe --abbrev=0)"
  git checkout tags/"$tag"
}

function installDependencies(){
  printf "\nInstalling dependencies...\n"
  sudo pip3 install -r requirements.txt
}

function main() {
  clean
  updateRepository
  installDependencies

  chmod +x install.sh update.sh

  echo "$(tput setaf 2)Update completed$(tput setaf 7)"
}

main