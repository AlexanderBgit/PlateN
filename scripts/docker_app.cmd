@echo off

PUSHD "..\deploy"
ECHO "STOPPING SEPARATED DEV DB CONTAINER"
docker stop fastparking-db-postgres-1
rem docker-compose  --file docker-compose-project.yml --env-file .env  up -d 
docker-compose  --file docker-compose-project.yml --env-file .env up  
POPD