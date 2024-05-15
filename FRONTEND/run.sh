#!/bin/sh

echo Sleep for 15 seconds to wait for the database to be ready
sleep 15
cd fastparking
pwd
echo RUN MIGRATION
USE_DS_NUMBER_DETECTION=0 python manage.py migrate
export PYTHONPATH=${PYTHONPATH}:./:./fastparking:/app/fastparking:/app
echo CREATE SPUREUSER
USE_DS_NUMBER_DETECTION=0 python ./admin/create_admin_user.py
echo CREATE PARKING PLACE
USE_DS_NUMBER_DETECTION=0 python ./parking/create_parking.py
echo RUN BACKGROUND SHEDULER
./cron_loop.sh &
echo RUN FRONTEND - DJANGO
python manage.py runserver 0.0.0.0:8000 --insecure

#bash

