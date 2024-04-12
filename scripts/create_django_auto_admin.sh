#!/bin/bash

# simulate poetry shell
pushd "../FRONTEND"
pyact=$(poetry env info -p)
source ${pyact}/bin/activate
popd
pushd "../FRONTEND/fastparking"
python ./admin/create_admin_user.py
popd