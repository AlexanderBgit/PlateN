#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"


ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE' ${ENV} | xargs) &> /dev/null


echo "LOGS OF  DB CONTAINER ${BRANCH:-}${PURPOSE:-}"


docker logs fastparking${BRANCH:-}${PURPOSE:-}-api-1 -t -f