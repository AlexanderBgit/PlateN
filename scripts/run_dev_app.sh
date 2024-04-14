#!/bin/bash

# simulate poetry shell
pushd "../FRONTEND"
git rev-parse --short HEAD > git-version.txt
pyact=$(poetry env info -p)
source ${pyact}/bin/activate
popd
pushd "../FRONTEND/fastparking"
python manage.py runserver 0.0.0.0:8000
popd