#!/bin/bash

pushd "../deploy"
# echo "STOPPING SEPARATED DEV DB CONTAINER"
# docker stop fastparking-db-postgres-1
git rev-parse --short HEAD > ../FRONTEND/git-version.txt
echo "STARTING"
docker-compose  --file docker-compose-project.yml --env-file .env up -d
popd