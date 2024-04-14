# PlateN
Plate license recognition

# Development environment

## env file
На основі файлу `deploy/env-examples` створюємо власний  `deploy/.env` з власними змінними

<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h2>LOCAL DEVELOPMENT</h2></summary>

- git проекту: https://github.com/AlexanderBgit/PlateN , default branch `dev`

- кожен створює власні гілки від `dev` і оновлює їх через `merge`. Іменна гілок `usernmae` - постійна користувача, `usernmae-feature` тимчасова, після об'єднання з іншими гілками знищується.

- merge to `dev` тільки через `pull-request` і запит користувачам на підтвердження, мінімум один має підтвердити, і тоді розблокується кнопка `Merge`, і можна об'єднати у `dev`.

- Python >=3.10,<3.12

- poetry

- Django 5

- Скрипти `.cmd` для виконання у операційній системі Windows тільки.

- Скрипти `.sh` для виконання у операційній системі Linux, Mac.

- Корінь git проекту має декілька незалежних підпроєктів:
    - BACKEND
    - FRONTEND
    - Database
    - DS

- Кожен підпроєкт - незалежний продукт, і відповідно має свій незалежний Docker. 

- Спілкуються через спільну базу даних, при розробці це може бути локальна з Docker або віддалена у elephantsql.

- Налаштування змінних середовища - спільні у файлі /deploy/.env. Локальна розробка використовує тільки відносний шлях до цього файлу. Наприклад код з `fastparking\fastparking\settings.py`: 
```
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR.parent.parent.joinpath("deploy").joinpath(".env")
if env_file.exists():
    load_dotenv(env_file) 
else:
    print("ENV file not found:", env_file)
```

- _Security_. Кожен докер при старті бере налаштування з .env котрі йому тільки потрібні, а не весь файл. Розміщується .env файл тільки за межами докер контейнера.

- FRONTEND має власне віртуальне оточення poetry.

- BACKEND має власне віртуальне оточення poetry

- DS - робочі файли для Data Science

- Для роботи з FRONTEND:
    - переходимо у теку FRONTEND, активуємо віртуальне сердобине `poetry shell`
    - Далі `poetry update` встановить або оновить пакунки субпроєкту.

- Для роботи з BACKEND:
    - переходимо у теку BACKEND, активуємо віртуальне сердобине `poetry shell`
    - Далі `poetry update` встановить або оновить пакунки субпроєкту.

- Якщо у VC Code створити Workspace, додати до нього підпроєкти як (File->Add folder to WorkSpace), то при запуску терміналу буде запити з якої теки ви це хочете зробити.

 - Для роботи з локальною базою даних використовуємо настуні кроки (Local Database postgres). Для роботи з віддаленою базою даних пропускаємо ці кроки.
</details>

<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h3>Local Database postgres</h3></summary>

#### run database postgres docker container

`scripts/docker_db.cmd`

Данні бази будуть створенні у теці `Database\postgres-data\`

Тека додана у виключення git - не викладати у git, у кожного вона своя!

#### stop database postgres docker container
`scripts\docker_db_stop.cmd`
</details>

<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h3>Запуск та обслуговування застосунку в докер</h3></summary>

#### run app locally
Запускати з віртуального оточення poetry
```
cd FRONTEND/fastparking
python manage.py runserver 0.0.0.0:8000
```
`scripts\run_dev_app.cmd`

#### export poetry package to requirements.txt
Запускати з віртуального оточення poetry
```
cd FRONTEND
poetry export --without-hashes > requirements.txt
```
`scripts\gen_req_txt.cmd`

#### migrate db changes
```
cd FRONTEND/fastparking
python manage.py migrate
```

#### Автоматичне створення супер адміністратора Django з оточення .env

`scripts\create_django_auto_admin.cmd`

#### Запуск всього проєкту з підпроєктами у докер

##### run project (db+code) docker container
Данні бази будуть створенні у теці `Database\postgres-data\`

`scripts\docker_app_run.cmd`

Режим DEBUG - консолі 

##### rebuild project (code) docker container
`scripts\docker_app_build.cmd`
</details>


<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h2>Процедура підключення dev - Django з нуля:</h2></summary>

1. git checkout dev
1. git pull
1. cd FRONTEND
1. poetry shell
1. poetry update
1. cd ..
1. cd scripts
1. docker_db.cmd - run DB local docker, skip if remote used postgres
1. migrate_dev_app.cmd - migrate DB
1. create_django_auto_admin.cmd - create admin aromatically from .env
1. run_dev_app.cmd - run app
1. open browser: http://127.0.0.1:8000
</details>

<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h2>SERVER SIDE DEPLOY - CI/CD</h2></summary>


<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h3>CI перевірка коду </h3></summary>


Перевірка коду проєкту на збирання проходить автоматично у кожному "GitHub pull request" безпосередньо перед об'єднанням з гілкою `dev` функцію Action GitHub.

Але без повірки міграції.

Action GitHub використовує налаштуванням з файлу `.github\workflows\django.yml` де проходить перевірка на збирання середовища виконання для трьох версії python:  `python-version: ["3.10", "3.11"]`. 

Безпосереднє тестування проєкту Django автоматично виконується командую `python manage.py test`.
</details>

<details>
  <summary style="display: flex; align-items: center; color: #0088CC;"><span style="margin-right: 5px;"></span><h3>CD </h3></summary>

Сервер: Linux (Debian).

Локальний користувач для виконання задач без прав адміністратора.

На сервері проект виконуються у декількох `docker` контейнерах, котрі об'єднані файлом налаштувань: `deploy\docker-compose-project.yml`.

Для визначення події з необхідності виконати операцію повторного `deploy` - періодично виконується скрипт: `scripts\detect_changes_git.sh`. 

Цей скрипт визначає чи не змінилася віддалена гілка проекту `dev`. 

Якщо зміни виявленні то виконується скрипт - `scripts\re_deploy_docker.sh`.

Для налаштувань під конкретні умови середовища виконання файл `detect_changes_git` копіюємо за межі теки проєкту.

У нас це рівень вище `~/PlateN/`, та змінюємо локальний шлях до теки проєкту у змінній `SOURCE`.  
```
SOURCE=${HOME}/PlateN/PlateN
```

Для налаштування системного планувальника завдань використано команду `crontab -e`.

Де додано наступний рядок: 
```
*/15 * * * *  ~/PlateN/detect_changes_git.sh > /dev/null 2>&1
```
 Що дозволяє запускати скрипт `detect_changes_git.sh` кожні 15 хвилин.
</details>

</details>

