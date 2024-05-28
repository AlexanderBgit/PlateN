@echo off
echo "runed poetry shell?"
@REM poetry env info -p
@REM echo "\Scripts\activate"
@REM PUSHD "../FRONTEND/fastparking"
poetry run python manage.py createsuperuser --username admin
POPD