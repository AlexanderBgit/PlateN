#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

ENV=../deploy/.env
[ ! -f ${ENV} ] ||  export $(grep -E '^STATIC_DEPLOY|^BRANCH' ${ENV} | xargs) 



pushd "../FRONTEND/fastparking"
ST_D=${STATIC_DEPLOY}/${BRANCH}
if [ ! -z "${STATIC_DEPLOY}" ] && [ -d ${ST_D} ];then
 echo -e "\nRSYNC STATIC DEPLOY..."
 rsync -a static ${ST_D}
else
 echo -e "\nRSYNC STATIC DEPLOY not found ${STATIC_DEPLOY}"
fi
popd