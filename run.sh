#!/bin/sh

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

docker run -it --rm \
    -v $SCRIPTPATH/output/:/output \
    -v $SCRIPTPATH/templates/:/templates \
	-v $SCRIPTPATH/this_weeks_teams.yml:/this_weeks_teams.yml \
	-v $SCRIPTPATH/TeamMap.yml:/TeamMap.yml \
	-e WHATSON_URL="https://w.fixtureslive.com/club/826/whats-on/Chertsey-Thames-Valley" \
	-e TYPE="fixtures" \
	`#-e TEMPLATE="Brad1.png"` \
	fl_image_generator:latest
	
	