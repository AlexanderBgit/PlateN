#!/bin/sh

echo Sleep for 15 seconds to wait for the database to be ready
sleep 15
cd fastparking
pwd
echo RUN MIGRATION
python manage.py migrate
export PYTHONPATH=${PYTHONPATH}:./:./fastparking:/app/fastparking:/app
echo CREATE_SPUREUSER
python ./admin/create_admin_user.py
echo RUN BACKGROUND SHEDULER
./cron_loop.sh &
echo RUN FRONTEND - DJANGO
python manage.py runserver 0.0.0.0:8000

#bash

