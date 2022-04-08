#!/bin/sh

echo "Starting softwares...."
librespot jq -v -n "Hela huset" --passthrough --backend pipe --device /spotify_stream &
ices /ices.xml < /spotify_stream &
icecast -c /icecast.xml
