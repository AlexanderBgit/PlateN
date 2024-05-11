#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
#  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

# ./gen_static.sh
./migrate_dev_app.sh
echo -e "\nStarting to check additional libraries..."
if find /usr/local/lib -name "libpoppler*" -print -quit 2>/dev/null; then
    echo "Poppler library files found."
else
    echo -e "\n*** Poppler library files not found. PDF function is limited in app. ***"
fi

# simulate poetry shell
pushd  "../FRONTEND"  > /dev/null
git rev-parse --short HEAD > git-version.txt
#pyact=$(poetry env info -p)
#source ${pyact}/bin/activate
popd > /dev/null
echo -e "\nStarting Django web server..."
pushd  "../FRONTEND/fastparking" > /dev/null
poetry run python manage.py runserver 0.0.0.0:8000  --insecure
popd > /dev/null