#!/bin/sh
cd /usr/local/src/detector/
../venv/bin/python servo 90 90
../venv/bin/python detector.py `rpicam-hello --list-cameras | egrep '^0' | awk '{print $3;}'`
