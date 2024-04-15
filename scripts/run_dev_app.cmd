@echo off
echo "runed poetry shell?"
poetry env info -p
echo "\Scripts\activate"
PUSHD "../FRONTEND/fastparking"
git rev-parse --short HEAD > ..\git-version.txt
python manage.py runserver 0.0.0.0:8000
POPD