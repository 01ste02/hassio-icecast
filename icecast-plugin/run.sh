#!/bin/sh

echo "Starting softwares...."
librespot jq -n TestHomeAssistant --backend pipe | ices /ices.xml &
icecast -c /icecast.xml
