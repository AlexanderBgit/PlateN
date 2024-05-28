#!/bin/sh

echo Sleep for 10 seconds to wait for the database to be ready
sleep 10
cd fastparking
pwd
echo RUN MIGRATION
USE_DS_NUMBER_DETECTION=0 python manage.py migrate
echo Starting Django collectstatic...
USE_DS_NUMBER_DETECTION=0 python manage.py collectstatic --noinput
export PYTHONPATH=${PYTHONPATH}:./:./fastparking:/app/fastparking:/app
echo CREATE GROUPS
USE_DS_NUMBER_DETECTION=0 python ./admin/create_groups.py
echo CREATE SPUREUSER AND OTHER USERS
USE_DS_NUMBER_DETECTION=0 python ./admin/create_admin_user.py
echo CREATE PARKING PLACE
USE_DS_NUMBER_DETECTION=0 python ./parking/create_parking.py
echo RUN BACKGROUND SHEDULER
./cron_loop.sh &

echo RUN FRONTEND - DJANGO
python manage.py runserver 0.0.0.0:8000 --insecure

#bash

