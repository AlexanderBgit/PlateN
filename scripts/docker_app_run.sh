#!/bin/zsh

pushd "../deploy"
docker-compose  --file docker-compose-project.yml --env-file .env  run --rm code
popc