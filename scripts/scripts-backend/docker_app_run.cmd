@echo off                                                                                                                                                   
PUSHD "..\..\deploy"
echo "Running docker BACKEND API"
docker compose  --file docker-compose-api.yml --env-file .env  run --rm api
POPD