import os
import re
import time
import requests
import hmac
import hashlib

from matrix_client.room import Room
from matrix_client.client import MatrixClient


class SynapseAPIClient:
    client_path = "_matrix/client/v3"
    discovery_room_alias = "discoveryroom"

    def __init__(self, base_url, login, password, token=""):
        self.base_url = base_url
        self.domain = base_url.replace("https://", "").replace("http://", "")
        self.domain_no_port = remove_after_last_colon(self.domain)
        self.login = login
        self.password = password
        if token == "":
            self.token = self._get_auth_token()
        else:
            self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get_auth_token(self):
        auth_url = f"{self.base_url}/{self.client_path}/login"
        credentials = {
            "identifier": {"type": "m.id.user", "user": self.login},
            "initial_device_display_name": "✒️ Script",
            "password": self.password,
            "type": "m.login.password",
        }

        response = requests.post(auth_url, json=credentials)
        response.raise_for_status()
        auth_data = response.json()
        return auth_data["access_token"]

    def getDiscoveryRoomId(self, url):
        remote_domain_no_port = domain_not_port(url)
        room_url = f"{self.base_url}/{self.client_path}/directory/room/%23{self.discovery_room_alias}%3A{remote_domain_no_port}"
        response = requests.get(room_url, headers=self.headers)
        response.raise_for_status()
        return response.json()["room_id"]

    def getAllUserFromHomeserver(self):
        room_url = (
            f"{self.base_url}/_synapse/admin/v2/users?from=0&limit=10000&guests=false"
        )
        response = requests.get(room_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_users(self):
        url = (
            f"{self.base_url}/_synapse/admin/v2/users?from=0&limit=1000000&guests=false"
        )
        res = requests.get(
            url=url,
            headers=self.headers,
        )
        if res.status_code != 200:
            raise Exception("Error when retrieving all users", res)
        parsed = res.json()
        return parsed["users"]

    def createDiscoveryRoom(self):
        request_url = f"{self.base_url}/_matrix/client/v3/createRoom"
        body = {
            "name": "Discovery Room",
            "power_level_content_override": {
                "events_default": 50,
                "invite": 50,
                "kick": 50,
                "state_default": 100,
                "users_default": 0,
            },
            "preset": "public_chat",
            "room_alias_name": f"{self.discovery_room_alias}",
            "room_version": "9",
            "visibility": "private",
            "join_rules": "public",
        }
        res = requests.post(url=request_url, json=body, headers=self.headers)
        return res.json()["room_id"]

    def get_users_in_room(self, room_id):
        """
        https://matrix-org.github.io/matrix-python-sdk/matrix_client.html#matrix_client.room.Room.get_joined_members
        """
        client = MatrixClient(self.base_url)
        client.login(username=self.login, password=self.password)

        room = Room(client, room_id)

        if not room:
            raise Exception("didn't find discovery room")
        return list(map(lambda user: user.user_id, room.get_joined_members()))

    def add_user_in_room(self, room_id, user_id):
        url = f"{self.base_url}/_synapse/admin/v1/join/%s" % room_id

        start_time = time.time()
        res = requests.post(
            url=url,
            json={
                "user_id": user_id,
            },
            headers=self.headers,
        )
        if res.status_code != 200:
            print(res)
            print(res.content)
            raise Exception(
                f"Error when joining the discovery room for user {user_id}", res
            )

        elapsed_time = time.time() - start_time
        print(f"     Total time Process for user {user_id}: {elapsed_time}")
        return elapsed_time

    def register_dummy_user(self):
        url = f"{self.base_url}/_synapse/admin/v1/register"
        nonce = requests.get(url).json()["nonce"]
        mac = generate_mac(
            nonce, os.environ["DUMMY_USER"], os.environ["DUMMY_PASSWORD"]
        )

        registration_res = requests.post(
            url,
            json={
                "nonce": nonce,
                "username": os.environ["DUMMY_USER"],
                "displayname": os.environ["DUMMY_USER"],
                "password": os.environ["DUMMY_PASSWORD"],
                "admin": False,
                "mac": mac,
            },
        ).json()

        if (
            registration_res["user_id"]
            == f"@{os.environ['DUMMY_USER']}:{self.domain_no_port}"
        ):
            print("Dummy user created")
        elif registration_res["errcode"] == "M_USER_IN_USE":
            print("User was already created")
        else:
            raise Exception("Error creating dummy user", registration_res)

        return

    def join_discoveryroom(self, remote_url):
        room_id = self.getDiscoveryRoomId(remote_url)
        url = f"{self.base_url}/_matrix/client/r0/join/{room_id}"

        if self.domain_no_port != remote_url:
            url = url + f"?server_name={remote_url}"

        res = requests.post(
            url,
            headers=self.headers,
            json={"reason": "dummy user joins discovery room"},
        )
        res.raise_for_status()
        print("Join remote discovery room : ok")


def domain_not_port(url):
    return remove_after_last_colon(url).replace("https://", "").replace("http://", "")


def remove_after_last_colon(url):
    if url.count(':') < 2:
        return url
    pattern = r"(.*):[^:]*$"
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    else:
        return url


def generate_mac(nonce, user, password, admin=False, user_type=None):
    mac = hmac.new(
        key=bytearray(os.environ["SYNAPSE_SECRET"].encode("utf8")),
        digestmod=hashlib.sha1,
    )

    mac.update(nonce.encode("utf8"))
    mac.update(b"\x00")
    mac.update(user.encode("utf8"))
    mac.update(b"\x00")
    mac.update(password.encode("utf8"))
    mac.update(b"\x00")
    mac.update(b"admin" if admin else b"notadmin")
    if user_type:
        mac.update(b"\x00")
        mac.update(user_type.encode("utf8"))

    return mac.hexdigest()
