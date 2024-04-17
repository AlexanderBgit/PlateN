@echo off
echo "runed poetry shell?"

echo "runing migration"

call migrate_dev_app.cmd

PUSHD "..\FRONTEND\fastparking"
poetry env info -p
echo "\Scripts\activate"
git rev-parse --short HEAD > ..\git-version.txt
python manage.py runserver 0.0.0.0:8000
POPD