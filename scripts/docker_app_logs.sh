#!/bin/bash

ENV=../deploy/.env
[ ! -f ${ENV} ] || export $(grep '^BRANCH' ${ENV} | xargs)


docker logs fastparking${BRANCH}-code-1 -t -f