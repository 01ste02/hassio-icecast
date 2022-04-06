#!/bin/bash

echo "Starting softwares...."
librespot -q -n TestHomeAssistant --backend pipe | ices /ices.xml &
icecast -c /icecast.xml
