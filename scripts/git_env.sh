#!/bin/bash

export PATH=/usr/local/bin:${PATH}

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

echo git config --global user.name=... $(git config user.name)
echo git config --global user.email=... $(git config user.email)
echo git remote set-url --push origin git@github.com:/..$(git remote -v)

eval $(ssh-agent -t 600)
echo  "LOADED SSH_AGENT_PID: ${SSH_AGENT_PID}... opened new BASH session, for exit use Ctrl-D or exit for kill ssh-agent"
bash
echo Killing ssh-agent...
eval $(ssh-agent -k)
