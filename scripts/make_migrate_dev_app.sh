#!/bin/bash

# simulate poetry shell
pushd "../FRONTEND"
pyact=$(poetry env info -p)
source ${pyact}/bin/activate
popd

echo PYTHONPATH=${PYTHONPATH}
pushd "../FRONTEND/fastparking"
python manage.py makemigrations
popd