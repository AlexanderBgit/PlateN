#!/bin/bash

export PATH=/usr/local/bin:${PATH}
export TERM=xterm

BRANCH=${BRANCH:-dev}
ROOTPATH=${ROOTPATH:-${HOME}/PlateN/}
SOURCE=${ROOTPATH}/PlateN-${BRANCH}
GIT_CMD="git --git-dir=${SOURCE}/.git --work-tree=${SOURCE}"
GIT_PRJ="https://github.com/AlexanderBgit/PlateN.git"

echo "CHECK GIT: branch - ${BRANCH} ${PURPOSE}"

if [ ! -d ${SOURCE} ]; then
 git clone ${GIT_PRJ} -b ${BRANCH} ${SOURCE}
 exit
fi


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
        ./re_deploy_docker.sh ${BRANCH}  > ${SOURCE}/../last_deployed_${BRANCH}.log
        popd
        echo `date` > ${SOURCE}/../last_deployed_${BRANCH}.txt

fi

