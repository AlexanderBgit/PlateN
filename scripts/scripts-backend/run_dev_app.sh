#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
#  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

ENV=../../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE|^APP_PORT_API' ${ENV} | xargs)

echo $(git branch --show-current)${PURPOSE}-$(git rev-parse --short HEAD) > ../../BACKEND/git-version.txt

echo -e "\nStarting FastAPI web server in dev mode with reload..."
pushd  "../../BACKEND/api" > /dev/null
poetry run uvicorn main:app --port ${APP_PORT_API:-9000} --host 0.0.0.0 --reload
popd > /dev/null