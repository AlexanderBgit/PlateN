#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

ENV=../../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^APP_PORT_API' ${ENV} | xargs)

pushd "../../deploy"
echo -e "\nRunning docker BACKEND API"

#docker compose  --file docker-compose-api.yml --env-file .env  \
# run --name fastparking-backend-api --build -p ${APP_PORT_API:-9000}:${APP_PORT_API:-9000} --rm api

docker compose  --file docker-compose-api.yml --env-file .env  up --build -d


popd