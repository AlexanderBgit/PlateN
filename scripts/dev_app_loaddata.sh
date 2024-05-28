#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

echo PYTHONPATH=${PYTHONPATH}
pushd "../FRONTEND/fastparking"

BACKUP_FILE="savedb.json.gz"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo  " file \"${BACKUP_FILE}\" is missing, cancel."
  popd
  exit 1
fi

echo -n "Want to rewrite all database from file \"${BACKUP_FILE}\"? (y/n): "
read answer

if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Rewriting the database..."
    # Your code to rewrite the database goes here
else
    echo "Operation canceled."
    popd
    exit 1
fi

echo -e "\nStarting Django loaddata..."
gzip -d -c "${BACKUP_FILE}" | USE_DS_NUMBER_DETECTION=0 python manage.py loaddata --format=json  -
popd