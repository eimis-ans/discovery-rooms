import requests

class SynapseAPIClient:
    client_path = '_matrix/client/v3'
    discovery_room_alias = 'discoveryroom'

    def __init__(self, base_url, login, password, token = ""):
            self.base_url = base_url
            self.server_name=base_url.replace("https://","")
            self.login = login
            self.password = password
            if token == "":
                self.token = self._get_auth_token()
            else:
                self.token = token
            self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def _get_auth_token(self):
            auth_url = f'{self.base_url}/{self.client_path}/login'
            credentials = {
                "identifier": {
                    "type": "m.id.user",
                    "user": self.login
                },
                "initial_device_display_name": "✒️ Script",
                'password': self.password,
                'type': 'm.login.password'
            }

            response = requests.post(auth_url, json=credentials)
            response.raise_for_status()
            auth_data = response.json()
            return auth_data['access_token']

    def getDiscoveryRoomId(self):
        room_url = f'{self.base_url}/{self.client_path}/directory/room/%23{self.discovery_room_alias}%3A{self.server_name}'
        response = requests.get(room_url, headers=self.headers)
        response.raise_for_status()
        return response.json()['room_id']
    
    def getAllUserFromHomeserver(self):
        room_url = f'{self.base_url}/_synapse/admin/v2/users?from=0&limit=10000&guests=false'
        response = requests.get(room_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def createRoom(self):
        return ''    