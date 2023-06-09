#!/usr/bin/python3

import os
import sys
import time
from dotenv import load_dotenv

from synapse_client import SynapseAPIClient


def parse_get_users(raw_user_name):
    return list(map(lambda x: x["name"], raw_user_name))


def run_procedure(admin_username, admin_password, synapse_url, remote_synapse_url, dry_run):

    print(f"""--- Run procedure ---
          admin user : {admin_username}
          synapse_url: {synapse_url}
          remote_synapse_url: {remote_synapse_url}
          dry_run: {dry_run}
          """)

    synapse_client = SynapseAPIClient(
        synapse_url, admin_username, admin_password)

    error_counts = 0
    try:
        print("Create dummy user if needed")
        synapse_client.register_dummy_user()

        discovery_room_id = synapse_client.getDiscoveryRoomId(synapse_url)
        if not discovery_room_id:
            print("Create discovery room...")
            discovery_room_id = synapse_client.createDiscoveryRoom()

        # get all users in home server (can be up to 100k)
        all_users_by_name = synapse_client.get_users()

        all_user_ids = parse_get_users(all_users_by_name)

        print("Users in homeserver : %s" % len(all_user_ids))

        # get all users in discovery room
        users_in_room = synapse_client.get_users_in_room(discovery_room_id)
        print(all_user_ids)

        print("Users in room (with dummy users): %s" % len(users_in_room))

        # list all users missing the room
        users_missing_in_room = set(
            all_user_ids).difference(set(users_in_room))
        print("Users missing in room : %s" % len(users_missing_in_room))

        # add user one by one
        for index, user_id in enumerate(users_missing_in_room):
            try:
                print(
                    f"{len(users_missing_in_room)}/{index + 1} Adding user {user_id} in room : {discovery_room_id}"
                )
                if not dry_run:
                    elapsed_time = synapse_client.add_user_in_room(
                        room_id=discovery_room_id, user_id=user_id
                    )
            except Exception as e:
                error_counts += 1
                if error_counts > 100:
                    raise Exception("too many errors, stopping process")
                print(e)
            time.sleep(
                1
            )  # use async programming instead : https://realpython.com/python-sleep/#adding-a-python-sleep-call-with-async-io

        dummy_client = SynapseAPIClient(
            synapse_url, os.environ["DUMMY_USER"], os.environ["DUMMY_PASSWORD"])
        dummy_client.join_discoveryroom(remote_synapse_url)

    except Exception as e:
        print(e)


def add_http_if_needed(url):
    return url if url.startswith("https://") or url.startswith("http://") else "https://" + url


if __name__ == "__main__":
    load_dotenv()

    dry_run = len(sys.argv) > 1 and sys.argv[1] == "dry-run"
    synapse_url = os.environ["SYNAPSE_URL"]
    remote_synapse_url = os.environ["REMOTE_SYNAPSE_URL"]
    admin_username = os.environ["ADMIN_USERNAME"]
    admin_password = os.environ["ADMIN_PASSWORD"]

    synapse_url = add_http_if_needed(synapse_url)

    remote_synapse_url = remote_synapse_url.replace(
        "https://", "").replace("http://", "")

    run_procedure(admin_username, admin_password, synapse_url=synapse_url,
                  remote_synapse_url=remote_synapse_url, dry_run=dry_run)
