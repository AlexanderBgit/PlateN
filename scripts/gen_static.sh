#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

pushd "../FRONTEND/fastparking"
echo -e "\nStarting Django collectstatic..."
poetry run python manage.py  collectstatic --noinput
popd