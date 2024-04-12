#!/bin/bash

./docker_app_build.sh
./docker_app_stop.sh
./docker_app.sh

count=`docker ps | grep fastparking- | wc -l`
if [ ${count} -lt 2 ]; then 
 ./docker_app.sh
fi

count=`docker ps | grep fastparking- | wc -l`
if [ ${count} -lt 2 ]; then 
 ./docker_app.sh
fi


