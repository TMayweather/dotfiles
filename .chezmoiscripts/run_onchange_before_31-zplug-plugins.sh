{{ $plugins := list
  "agpenton/1password-zsh-plugin"
  "zshzoo/cd-ls"
  "zsh-users/zsh-history-substring-search"
  "zdharma-continuum/fast-syntax-highlighting"
  "plugins/autojump", from:oh-my-zsh
-}}

#!/usr/bin/env bash
function is_zsh_installed() {
  command -v zsh > /dev/null
}

function run_zsh_command() {
  $(command -v zsh) -c "$1"
}

function update_zplug_plugins() {
  echo "Updating zplug plugins..."
  run_zsh_command "zplug update" &> /dev/null
}

function is_zplug_plugin_installed() {
  run_zsh_command "zplug list $1" &> /dev/null
}

function install_zplug_plugin() {
  run_zsh_command "zplug install $1"
}

function install_zplug_plugins() {
  {{- range $plugin := $plugins }}
  if ! is_zplug_plugin_installed "{{ $plugin }}"; then
    install_zplug_plugin "{{ $plugin }}"
  fi
  {{- end }}
}

function main() {
  if is_zsh_installed ; then
    install_zplug_plugins
    update_zplug_plugins
  fi
}

if [[ ${#BASH_SOURCE[@]} = 1 ]]; then
  main
fi
