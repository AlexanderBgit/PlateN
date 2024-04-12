#!/bin/sh

./docker_app_build.sh
./docker_app_stop.sh
sleep 10
./docker_app.sh


