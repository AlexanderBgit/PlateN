@echo off

PUSHD "..\deploy"
ECHO "STOPPING SEPARATED DEV DB CONTAIMNINER"
docker stop fastparking-db-postgres-1
cd 
dir
rem docker-compose  --file docker-compose-project.yml --env-file .env  up -d 
docker-compose  --file docker-compose-project.yml --env-file .env up 
POPD