#!/usr/bin/python3

import os
import requests
import time
from dotenv import load_dotenv

# from tinydb import TinyDB, Query
from matrix_client.api import MatrixHttpApi
from matrix_client.room import Room
from matrix_client.client import MatrixClient

from synapse_client import SynapseAPIClient

def mock_post(index, fail):
    res = lambda: None
    res.status_code = 200
    if fail and index in [23, 33, 45]:
        res.status_code = 401
    return res


def get_users_in_room_by_token(synapse_url, room_id, access_token):
    '''
        https://matrix-org.github.io/matrix-python-sdk/matrix_client.html#matrix_client.room.Room.get_joined_members
    '''
    print(f"Connect client with access token")
    client = MatrixClient(synapse_url, access_token)

    # get a room
    room = Room(client, room_id)

    # get joined members
    return list(map(lambda user: user.user_id, room.get_joined_members()))


def get_users_in_room_by_pwd(synapse_url, dummy_username, dummy_user_password, room_id):
    '''
        https://matrix-org.github.io/matrix-python-sdk/matrix_client.html#matrix_client.room.Room.get_joined_members
    '''

    print(f"Connect client with password")
    client = MatrixClient(synapse_url)
    client.login_with_password(username=dummy_username, password=dummy_user_password)

    # get room
    room = Room(client, room_id)

    
    if not room:
        print(f"Create room")
        room = client.create_room(room_id)
    else:
        print("Room already exists")

    sys.exit(1)

    # get joined members
    return list(map(lambda user: user.user_id, room.get_joined_members()))


def mock__get_users_in_room(all_user_ids):
    return all_user_ids[0:100]


def get_users(admin_access_token, synapse_url):
    url = synapse_url + "/_synapse/admin/v2/users?from=0&limit=1000000&guests=false"
    # url = "http://localhost:8008/_synapse/admin/v2/users?from=0&limit=1000000&guests=false"
    print(f"Getting user from {url}")
    headers = {
        "Authorization": "Bearer %s" % admin_access_token,
    }
    res = requests.get(
        url=url,
        headers=headers,
    )
    if res.status_code != 200:
        raise Exception("Error when retrieving all users", res)
    parsed = res.json()
    return parsed["users"]


def parse_get_users(raw_user_name):
    return list(map(lambda x: x['name'], raw_user_name));


def mock__get_users(admin_access_token):
    users = []
    for i in range(20000):
        users.append(
            {"name": f"@dummy:matrix.myserver.org"}
        )
    return users


def add_user_in_room(room_id, admin_access_token, user_id, synapse_url):
    url = synapse_url + "/_synapse/admin/v1/join/%s" % room_id
    # url = "http://localhost:8008/_synapse/admin/v1/join/%s" % room_id
    # print(f"Adding user {userId} in room : {room_id}")
    headers = {
        "Authorization": "Bearer %s" % admin_access_token,
    }

    start_time = time.time()
    # res = mock_post(index, False)
    res = requests.post(
        url=url,
        json={
            "user_id": user_id,
        },
        headers=headers,
    )
    if res.status_code != 200:
        print(res)
        print(res.content)
        raise Exception(f"Error when joining the discovery room for user {user_id}", res)

    elapsed_time = time.time() - start_time
    # elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    print(f"Total Process for user {user_id}: {elapsed_time}")
    return elapsed_time


def run_procedure(admin_access_token, room_id, dummy_username, dummy_user_password, mock_flag, synapse_url):
    error_counts = 0
    print(
        f"Run procedure with admin_access_token:%s, room_id:%s, synapse_url:%s, dummy_username:%s, dummy_user_password:%s, mock_flag:%s" % (
        admin_access_token, room_id, synapse_url, dummy_username, dummy_user_password, mock_flag))
    try:
        # get all users in home server (can be up to 100k)
        if mock_flag:
            all_users_by_name = mock__get_users(admin_access_token)
        else:
            all_users_by_name = get_users(admin_access_token, synapse_url)

        all_user_ids = parse_get_users(all_users_by_name)

        print("Users in homeserver : %s" % len(all_user_ids))

        # get all users in discovery room
        if mock_flag:
            users_in_room = mock__get_users_in_room(all_user_ids=all_user_ids)
        else:
            users_in_room = get_users_in_room_by_pwd(synapse_url=synapse_url, dummy_username=dummy_username,
                                                     dummy_user_password=dummy_user_password, room_id=room_id)
            # users_in_room = get_users_in_room_by_token(synapse_url=synapse_url,room_id=room_id, access_token=admin_access_token)

        print("Users in room (with dummy users): %s" % len(users_in_room))

        # list all users missing the room
        users_missing_in_room = set(all_user_ids).difference(set(users_in_room))
        users_missing_in_room_len = len(users_missing_in_room)
        print("Users missing in room : %s" % users_missing_in_room_len)

        # add user one by one
        for index, user_id in enumerate(users_missing_in_room):

            try:
                print(f"{users_missing_in_room_len}/{index + 1} Adding user {user_id} in room : {room_id}")
                elapsed_time = add_user_in_room(admin_access_token=admin_access_token, room_id=room_id, user_id=user_id,
                                                synapse_url=synapse_url)
                print()
            except Exception as e:
                error_counts += 1
                if (error_counts > 100):
                    raise Exception("too many errors, stopping process")
                print(e)
            time.sleep(
                1)  # use async programming instead : https://realpython.com/python-sleep/#adding-a-python-sleep-call-with-async-io


    except Exception as e:
        print(e)


if __name__ == '__main__':

    load_dotenv()

    admin_access_token = os.environ["ADMIN_ACCESS_TOKEN"]
    synapse_url = os.environ["SYNAPSE_URL"]
    room_id = os.environ["DISCOVERY_ROOM_ID"]
    dummy_username = os.environ["DUMMY_USERNAME"]
    dummy_user_password = os.environ["DUMMY_PASSWORD"]

    synapse_url = synapse_url if synapse_url.startswith("https://") else "https://" + synapse_url
    mock_flag = False

    run_procedure(admin_access_token, room_id, dummy_username, dummy_user_password, mock_flag=mock_flag,
                  synapse_url=synapse_url)
