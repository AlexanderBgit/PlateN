#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE' ${ENV} | xargs)


echo "Load data OF CONTAINER ${BRANCH:-}${PURPOSE:-}"

docker cp savedb.json.gz fastparking${BRANCH:-}${PURPOSE:-}-code-1:/appfastparking/savedb.json.gz"

docker exec -it  fastparking${BRANCH:-}${PURPOSE:-}-code-1 \
 bash -c "cd app/fastparking;ungzip savedb.json.gz | USE_DS_NUMBER_DETECTION=0 python manage.py loaddata"


