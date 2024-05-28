@echo off                                                                                                                                                   
PUSHD "..\..\deploy"
echo "Running docker BACKEND API"
@REM docker compose  --file docker-compose-api.yml --env-file .env  run --rm api
docker compose  --file docker-compose-api.yml --env-file .env  up --build -d
POPD