#!/bin/zsh

pushd "../deploy"
docker-compose  --file docker-compose-api.yml --env-file .env  run --rm api
popc