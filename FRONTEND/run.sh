#!/bin/sh

echo Sleep 2 Waiting DB...
sleep 2
cd fastpakring
python manage.py migrate
echo Sleep 2 Migration...
sleep 2
python manage.py runserver 0.0.0.0:8000
