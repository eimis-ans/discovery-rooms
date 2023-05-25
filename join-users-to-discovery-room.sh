#!/bin/bash
export LANG=en_US.UTF-8
source discoveryroom_vars.sh
source venv/bin/activate
python3 main.py "${ADMIN_ACCESS_TOKEN}" "${DISCOVERY_ROOM_ID}" "@${DUMMY_USERNAME}:${SYNAPSE_URL}" "${DUMMY_PASSWORD}" "${SYNAPSE_URL}" > /tmp/join-users-to-discovery-room.log 2>&1
