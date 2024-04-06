# PlateN
Plate license recognition

# Development environment

## env file
На основі файлу `deploy/env-examples` створюємо власний  `deploy/.env` з власними змінними

## run database postgres docker container
`scripts/docker_db.cmd`
Данні бази будуть створенні у теці `Database\postgres-data\`
Тека додана у виключення git - не виладувати, у кожного вона своя!

## stop database postgres docker container
`scripts\docker_db_stop.cmd`

## run project (db+code) docker container
Данні бази будуть створенні у теці `Database\postgres-data\`
`scripts\docker_app_run.cmd`

## rebuild project (code) docker container
`scripts\docker_app_build.cmd`
