#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

pushd "../deploy"
docker-compose --file docker-compose-db.yml --env-file .env  up -d 
popd