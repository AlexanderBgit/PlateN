#!/bin/bash

pushd "../deploy"
docker-compose  --file docker-compose-project.yml --env-file .env build code
popd