@echo off
PUSHD "../FRONTEND/fastparking"
echo .
echo Starting Django collectstatic...
poetry run python manage.py collectstatic --noinput
POPD
POPD