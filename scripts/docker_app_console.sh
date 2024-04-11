#!/bin/zsh

pushd "../deploy"
echo "STOPPING SEPARATED DEV DB CONTAINER"
docker stop fastparking-db-postgres-1
docker-compose  --file docker-compose-project.yml --env-file .env up
popd