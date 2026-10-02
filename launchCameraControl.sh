#!/bin/sh
cd /usr/local/src/cameraControl/
../venv/bin/python servo.py 90 90
../venv/bin/python main.py `rpicam-hello --list-cameras | egrep '^0' | awk '{print $3;}'`
