#!/bin/bash
source venv/bin/activate
python3 src/main.py > ./join-users-to-discovery-room.log 2>&1
