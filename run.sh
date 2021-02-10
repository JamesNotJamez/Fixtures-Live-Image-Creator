#!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

docker run -it --rm \
       -v $SCRIPTPATH/output/:/output \
       -v $SCRIPTPATH/teams.yml:/teams.yml \
       -e TYPE="fixtures" \
       -e TEMPLATE="Brad1.png" \
       insta_master:latest

#       -v /Users/jamesralph/Documents/Coding/teams.yml:/teams.yml \
#       insta_fixtures_images:latest
