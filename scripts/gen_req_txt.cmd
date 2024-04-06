@echo off
echo "runed poetry shell?"
poetry env info -p
echo "\Scripts\activate"
PUSHD ../FRONTEND/fastparking
poetry export --without-hashes > requirements.txt
POPD