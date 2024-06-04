#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE' ${ENV} | xargs)  &> /dev/null


echo "SHELL OF DEV DB CONTAINER ${BRANCH:-}${PURPOSE:-}"


docker exec -it  fastparking${BRANCH:-}${PURPOSE:-}-code-1 bash