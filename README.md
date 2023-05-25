# discovery-rooms
some scripts to automate the creation of discovery rooms mecanism on matrix server

#How to run 
- create a Python virtual env : 
    ```bash
    python -m venv venv
    ```
- install puthon dependencies : 
    ```bash
    pip install -r requirements.txt
    ```
- copy the discoveryroom_vars_template.sh and fill it with values
    ```bash
    cp discoveryroom_vars_template.sh discoveryroom_vars.sh
    vim discoveryroom_vars.sh
    ```
- then run the join-users-to-discovery-room.sh script
    ```bash
    ./join-users-to-discovery-room.sh
    ```
  The result will be displayed in the /tmp/join-users-to-discovery-room.log file