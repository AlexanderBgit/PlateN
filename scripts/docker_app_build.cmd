@echo off                                                                                                                                                   
PUSHD "..\deploy"

docker-compose  --file docker-compose-project.yml --env-file .env build code 
rem timeout 1
rem docker attach fastparking-code-1

rem docker-compose down 

POPD