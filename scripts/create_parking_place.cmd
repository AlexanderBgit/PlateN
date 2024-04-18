@echo off
echo "runed poetry shell?"
PUSHD "../FRONTEND/fastparking"
poetry env info -p
echo "\Scripts\activate"
set PYTHONPATH=.
python ./parking/create_parking.py
POPD