# discovery-rooms

some scripts to automate the creation of discovery rooms mechanism on matrix server

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

- then run the join-users-to-discovery-room.sh script

    ```bash
    ./join-users-to-discovery-room.sh
    ```

  The result will be displayed in the /tmp/join-users-to-discovery-room.log file
