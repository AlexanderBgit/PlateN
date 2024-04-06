@echo off
echo "runed poetry shell?"
poetry env info -p
echo "\Scripts\activate"
PUSHD ../FRONTEND/fastparking
python manage.py runserver 0.0.0.0:8000
POPD