@echo off
echo ""
echo  "Starting Django makemigrations..."
PUSHD "../FRONTEND/fastparking"
poetry run python manage.py makemigrations
POPD