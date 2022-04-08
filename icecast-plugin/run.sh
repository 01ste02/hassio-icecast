#!/bin/sh

echo "Starting softwares...."
librespot jq -v -n HelaHemmet --passthrough --backend pipe | ices /ices.xml &
icecast -c /icecast.xml
