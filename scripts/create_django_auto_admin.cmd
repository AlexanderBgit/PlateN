@echo off
echo "runed poetry shell?"
poetry env info -p
echo "\Scripts\activate"
PUSHD "../FRONTEND/fastparking"
python ./admin/create_admin_user.py
POPD