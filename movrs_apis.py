import requests
import json

import subprocess

USER_EMAIL = ''
ACCESS_TOKEN = ''
TOKEN_TYPE = ''
USER_DATA =''
USER_ID = ''
BASEURL = 'https://eventmanagement-787937537053.us-central1.run.app'
BASEURL = 'http://127.0.0.1:6901'

def login_user(email, password):
    global USER_EMAIL, ACCESS_TOKEN, TOKEN_TYPE, USER_ID
    url = BASEURL + '/auth/login'
    data = {
        'email': email,
        'password': password
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)

        response_data = response.json()
        print("Login response:", response.text)

        if not response_data or 'access_token' not in response_data:
            print("Login failed: No access token in response.")
            return False

        USER_EMAIL = email
        ACCESS_TOKEN = response_data.get('access_token')
        TOKEN_TYPE = response_data.get('token_type')
        USER_ID = response_data.get('user_id')

        print(f"Login successful. User ID: {USER_ID}")
        update_json_fields([['logged_user_id',USER_ID],['email',USER_EMAIL],['password',password]], "user_cred.json")
        get_user_data(USER_ID)
        return True

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    return False


def get_user_info():
    return USER_DATA

def get_user_data(USER_ID):
    global USER_DATA
    url = BASEURL+'/users/get-user-data'
    data = {
        'user_id': USER_ID,
    }
    response = requests.post(url, json=data)  
    response_data=  response.json()
    USER_DATA =response_data
    return USER_DATA


def read_json_file(filepath="current_state.json"):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading state file: {e}")
        return None, None
    

def update_json_fields(pairs, filepath="current_state.json"):
    """
    Update multiple key-value pairs in a JSON file.
    
    Args:
        pairs: 2D array like [['state', 'running'], ['version', '1.0.3']]
        filepath: Path to the JSON file
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        for key, value in pairs:
            data[key] = value

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        return True
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error updating JSON file: {e}")
        return False
    


def run_docker_compose(detach=True, filepath="docker-compose.yml"):
    """
    Runs docker-compose in a separate process.

    Args:
        detach (bool): Whether to run in detached mode (`-d`)
        filepath (str): Path to the docker-compose.yml file
    """
    command = ["docker-compose", "-f", filepath, "up"]
    if detach:
        command.append("-d")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Docker Compose started with PID {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start docker-compose: {e}")
        return None