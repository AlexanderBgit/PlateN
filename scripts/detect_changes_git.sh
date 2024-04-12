#!/bin/env bash

SOURCE=${HOME}/PlateN/PlateN
GIT_CMD="git --git-dir=${SOURCE}/.git --work-tree=${SOURCE}"
BRANCH=dev


${GIT_CMD} checkout ${BRANCH} --quiet
${GIT_CMD} stash --quiet
${GIT_CMD} fetch --quiet

if ! ${GIT_CMD} diff origin/${BRANCH} --quiet
then
        ## for changes to stick, you need to pull them otherwise it will always have changes
        ${GIT_CMD} pull --quiet
        echo  do stuff
        pushd  ${SOURCE}/scripts
        chmod +x *.sh
        ./re_deploy_docker.sh
        popd
        `date` > ${SOURCE}/../last_deployed.txt
fi

