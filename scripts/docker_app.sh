#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
  dos2unix ../FRONTEND/*.sh &> /dev/null
  dos2unix ../BACKEND/*.sh &> /dev/null
fi

ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE' ${ENV} | xargs) &> /dev/null

pushd "../deploy"
echo $(git branch --show-current)${PURPOSE}-$(git rev-parse --short HEAD) > ../FRONTEND/git-version.txt
echo $(git branch --show-current)${PURPOSE}-$(git rev-parse --short HEAD) > ../BACKEND/git-version.txt
cp ../BACKEND/git-version.txt ../FRONTEND/git-version-backend.txt
grep -E "^\[tool.poetry\]$|^version" ../BACKEND/pyproject.toml > ../FRONTEND/backend-version.txt
echo "STARTING ${BRANCH}${PURPOSE}"
docker-compose  --file docker-compose-project.yml --env-file .env up -d
popd
sleep 5
./rsync_static.sh