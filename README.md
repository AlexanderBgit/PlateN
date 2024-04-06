# PlateN
Plate license recognition

# Development environment

## env file
На основі файлу `deploy/env-examples` створюємо власний  `deploy/.env` з власними змінними


## LOCAL DEVELOPMENT

### run database postgres docker container
`scripts/docker_db.cmd`
Данні бази будуть створенні у теці `Database\postgres-data\`
Тека додана у виключення git - не викладати у git, у кожного вона своя!

### stop database postgres docker container
`scripts\docker_db_stop.cmd`

### run app locally
Запускати з віртуального оточення poetry
```
cd FRONTEND/fastparking
python manage.py runserver 0.0.0.0:8000
```
### export poetry package to requirements.txt
Запускати з віртуального оточення poetry
```
cd FRONTEND
poetry export --without-hashes > requirements.txt
```
`scripts\run_dev_app.cmd`

### DOCKER ALL PROJECT

#### run project (db+code) docker container
Данні бази будуть створенні у теці `Database\postgres-data\`
`scripts\docker_app_run.cmd`

Режим DEBUG - консолі 

#### rebuild project (code) docker container
`scripts\docker_app_build.cmd`
