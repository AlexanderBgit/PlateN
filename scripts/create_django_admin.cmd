@echo off
echo "runed poetry shell?"
poetry env info -p
echo "\Scripts\activate"
PUSHD "../FRONTEND/fastparking"
python manage.py createsuperuser --username admin
POPD