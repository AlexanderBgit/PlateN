#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"


ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE' ${ENV} | xargs)


echo "LOGS OF  DB CONTAINER ${BRANCH:-}${PURPOSE:-}"


docker logs fastparking${BRANCH:-}${PURPOSE:-}-code-1 -t -f