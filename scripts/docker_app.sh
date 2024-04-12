#!/bin/env bash

pushd "../deploy"
# echo "STOPPING SEPARATED DEV DB CONTAINER"
# docker stop fastparking-db-postgres-1
echo "STARTING"
pwd
env
whereis docker-compose
docker-compose  --file docker-compose-project.yml --env-file .env up -d

popd