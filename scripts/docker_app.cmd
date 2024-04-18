@echo off

PUSHD "..\deploy"
ECHO "STOPPING SEPARATED DEV DB CONTAINER"
docker stop fastparking-db-postgres-1
git rev-parse --short HEAD > ..\FRONTEND\git-version.txt
rem docker-compose  --file docker-compose-project.yml --env-file .env  up -d 
docker-compose  --file docker-compose-project.yml --env-file .env up  
POPD