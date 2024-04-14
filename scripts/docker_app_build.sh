#!/bin/env bash

pushd "../deploy"
git rev-parse --short HEAD > ../FRONTEND/git-version.txt
docker-compose  --file docker-compose-project.yml --env-file .env build code
popd