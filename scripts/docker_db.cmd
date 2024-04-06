@echo off
PUSHD "../deploy"
docker-compose --file docker-compose-db.yml --env-file .env  up -d 
POPD