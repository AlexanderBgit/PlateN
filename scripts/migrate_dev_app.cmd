@echo off
echo.
echo Starting Django migrate...
PUSHD "../FRONTEND/fastparking"
SETLOCAL
SET USE_DS_NUMBER_DETECTION=0 
poetry run python manage.py migrate
ENDLOCAL
POPD