#!/bin/sh

echo "Starting softwares...."
librespot -n TestHomeAssistant --backend pipe | ices /ices.xml &
icecast -c /icecast.xml
