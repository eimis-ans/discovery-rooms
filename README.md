# discovery-rooms

A script to automate the creation of a discovery room and add all users to it.

⚠️ _A **not** scalable way for users to discover and contact people from other matrix instances_

## How to run

- create a Python virtual env :

  ```bash
  python -m venv venv
  ```

- install python dependencies :

  ```bash
  pip install -r requirements.txt
  ```

- copy the .env_template and fill it with values

  ```bash
  cp .env_template .env
  vim .env
  ```

- give it a try

  ```bash
  python3 src/main.py dry-run
  ```

  (it will still create the `discoveryroom` and `dummy_user` if they don't exist)

- then run the join-users-to-discovery-room.sh script

  ```bash
  ./join-users-to-discovery-room.sh
  ```

  The result will be displayed in the /tmp/join-users-to-discovery-room.log file
