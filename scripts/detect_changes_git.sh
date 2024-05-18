#!/bin/bash

export PATH=/usr/local/bin:${PATH}
export TERM=xterm

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

export BRANCH=dev
./detect_changes_git_branch.sh