#!/usr/bin/bash
# Description: Install Now-Playing software (github.com/feram18/now-playing)

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function installMatrixLibrary() {
  printf "\nInstalling rpi-rgb-led-matrix library...\n"
  cd "${ROOT_DIR}/rpi-rgb-led-matrix/" || exit
  make build-python PYTHON="$(command -v python3)"
  sudo make install-python PYTHON="$(command -v python3)"
  cd "${ROOT_DIR}" || exit
}

main() {
  echo "$(tput setaf 7)_________________________________________________________"
  echo "$(tput setaf 2) _   _                ______ _             _             "
  echo "$(tput setaf 2)| \ | |               | ___ \ |           (_)            "
  echo "$(tput setaf 2)|  \| | _____      __ | |_/ / | __ _ _   _ _ _ __   __ _ "
  echo "$(tput setaf 2)| . \` |/ _ \ \ /\ / / |  __/| |/ _\` | | | | | '_ \ / _\` |"
  echo "$(tput setaf 2)| |\  | (_) \ V  V /  | |   | | (_| | |_| | | | | | (_| |"
  echo "$(tput setaf 2)\_| \_/\___/ \_/\_/   \_|   |_|\__,_|\__, |_|_| |_|\__, |"
  echo "$(tput setaf 2)                                      __/ |         __/ |"
  echo "$(tput setaf 2)                                     |___/         |___/ "
  echo "$(tput setaf 7)_________________________________________________________"

  echo -e "$(tput setaf 7)\nUpdating system & installing Python 3"
  sudo apt-get update && sudo apt install python3-dev -y

  installMatrixLibrary

  echo -e "\n$(tput setaf 2)If there are no errors shown above, installation was successful."
  echo "$(tput setaf 7)To make sure your matrix is working properly, execute the samples located in ./rpi-rgb-led-matrix/bindings/python/samples"

  exit
}

main