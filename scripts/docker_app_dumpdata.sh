#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep -E '^BRANCH|^PURPOSE' ${ENV} | xargs)


echo "Dumpdata OF CONTAINER ${BRANCH:-}${PURPOSE:-}"

docker exec -it  fastparking${BRANCH:-}${PURPOSE:-}-code-1 \
 bash -c "cd app/fastparking;USE_DS_NUMBER_DETECTION=0 python manage.py dumpdata | gzip > savedb.json.gz"

docker cp -it  fastparking${BRANCH:-}${PURPOSE:-}-code-1:/appfastparking/savedb.json.gz savedb.json.gz"
