#!/bin/sh

echo Sleep 10 Waiting DB...
sleep 10
ls -la *
cd fastparking
echo RUN MIGRATION
python manage.py migrate
echo Sleep 2 Migration...
sleep 2
pwd
export PYTHONPATH=${PYTHONPATH}:./:./fastparking:/app/fastparking:/app
echo RUN BACKGROUND CRON-BOT
./cron_loop.sh &
echo RUN FRONTEND DJANGO
python manage.py runserver 0.0.0.0:8000

#bash

