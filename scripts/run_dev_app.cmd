@echo off
echo "runed poetry shell?"

PUSHD "..\FRONTEND\fastparking"
poetry env info -p
echo "\Scripts\activate"
git rev-parse --short HEAD > ..\git-version.txt
python manage.py runserver 0.0.0.0:8000
POPD