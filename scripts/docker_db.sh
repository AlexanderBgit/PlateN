#!/bin/bash

pushd "../deploy"
docker-compose --file docker-compose-db.yml --env-file .env  up -d 
popd