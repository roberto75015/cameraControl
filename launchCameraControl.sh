#!/bin/sh
cd /usr/local/src/detector/
../venv/bin/python detector.py `rpicam-hello --list-cameras | egrep '^0' | awk '{print $3;}'`
