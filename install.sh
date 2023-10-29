#!/usr/bin/env bash

set -e # -e: exit on error

function is_brew_installed() {
  command -v brew > /dev/null
}

function is_zplug_installed() {
  command --version zplug > /dev/null
}

function is_asdf_installed() {
  command --version asdf > /dev/null
}

function is_chezmoi_installed() {
  command -v chezmoi > /dev/null
}

function install_asdf_plugin() {
  asdf plugin add "$1"
  asdf install "$1" latest
  asdf global "$1" latest
}

function apply_dotfiles() {
  chezmoi=$(command -v chezmoi)
  script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null && pwd )"
  "${chezmoi}" init --apply "--source=${script_dir}"
}

function main() {
  if ! is_brew_installed ; then
    echo "Installing brew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi

  if ! is_zplug_installed ; then
    echo "Installing zplug..."
    brew install zplug
  fi

  if ! is_asdf_installed ; then
    echo "Installing asdf..."
    git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.8.0
    echo ". $HOME/.asdf/asdf.sh" >> ~/.zshrc  # Adjust for your shell
  fi

  if ! is_chezmoi_installed ; then
    echo "Installing chezmoi..."
    brew install chezmoi
  fi

  apply_dotfiles
}

if [[ ${#BASH_SOURCE[@]} = 1 ]]; then
  main
fi
