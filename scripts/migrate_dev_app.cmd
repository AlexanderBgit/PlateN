@echo off
@REM echo "runed poetry shell?"
PUSHD "../FRONTEND/fastparking"
poetry run python manage.py migrate
POPD