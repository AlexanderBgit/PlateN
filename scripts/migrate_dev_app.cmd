@echo off
echo.
echo Starting Django migrate...
PUSHD "../FRONTEND/fastparking"
poetry run python manage.py migrate
POPD