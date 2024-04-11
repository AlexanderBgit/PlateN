#!/bin/bash

pushd "../deploy"
echo "STOPPING SEPARATED DEV DB CONTAINER"
docker stop fastparking-code-1
docker stop fastparking-pg-1
docker-compose  --file docker-compose-project.yml --env-file .env down
popd