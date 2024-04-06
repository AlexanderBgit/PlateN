@echo off
echo "runed poetry shell?"
PUSHD "../FRONTEND/fastparking"
python manage.py migrate
POPD