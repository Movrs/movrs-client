import requests
import json
import os
import subprocess
import yaml 
import sys



USER_EMAIL = ''
ACCESS_TOKEN = ''
TOKEN_TYPE = ''
USER_DATA =''
USER_ID = ''
BASEURL = 'https://eventmanagement-787937537053.us-central1.run.app'
# BASEURL = 'http://0.0.0.0:6901'

# Determine the base directory of the installed package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    print(USER_ID)
    global USER_DATA
    url = BASEURL+'/users/get-user-data'
    data = {
        'user_id': USER_ID,
    }
    response = requests.post(url, json=data)  
    response_data=  response.json()
    USER_DATA =response_data
    print(USER_DATA)
    return USER_DATA


def read_json_file(filepath="current_state.json"):
    # Use absolute path for known files
    if filepath in ("current_state.json", "user_cred.json"):
        filepath = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(filepath):
        print(f"File '{filepath}' does not exist. Creating it.")
        with open(filepath, "w") as f:
            if(os.path.basename(filepath)=="current_state.json"):
                json.dump({"state": "running"}, f)
            else:
                json.dump({}, f)
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{filepath}': {e}")
        return None

def update_json_fields(pairs, filepath="current_state.json"):
    # Use absolute path for known files
    if filepath in ("current_state.json", "user_cred.json"):
        filepath = os.path.join(BASE_DIR, filepath)
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
    
def get_images_from_compose(file_path=None):
    if file_path is None or file_path == "docker-compose.yml":
        file_path = os.path.join(BASE_DIR, "docker-compose.yml")
    elif not os.path.isabs(file_path):
        file_path = os.path.join(BASE_DIR, file_path)
    with open(file_path, 'r') as f:
        compose_data = yaml.safe_load(f)

    services = compose_data.get("services", {})
    images = []
    for service in services.values():
        image = service.get("image")
        if image:
            images.append(image)
    return images

def image_exists_locally(image_name):
    result = subprocess.run(["docker", "images", "-q", image_name], capture_output=True, text=True)
    return result.stdout.strip() != ""
def run_missing_handler_script(script_path=None):
    if script_path is None or script_path == "movrs_client/app_updater.py":
        script_path = os.path.join(BASE_DIR, "app_updater.py")
    elif not os.path.isabs(script_path):
        script_path = os.path.join(BASE_DIR, script_path)
    print("Some Docker images are missing. Running download script...")
    subprocess.run([sys.executable, script_path])

def run_docker_compose(detach=True, filepath=None):
    if filepath is None or filepath == "docker-compose.yml":
        filepath = os.path.join(BASE_DIR, "docker-compose.yml")
    elif not os.path.isabs(filepath):
        filepath = os.path.join(BASE_DIR, filepath)
    try:
        print("File Path", filepath)
        images = get_images_from_compose(filepath)
    except FileNotFoundError:
        print("docker-compose.yml not found.")
        return

    missing_images = [img for img in images if not image_exists_locally(img)]

    if missing_images:
        print("Missing images:", missing_images)
        run_missing_handler_script()
        return
    else:
        print("All Docker images are available locally.")

    command = ["sudo","docker","compose","up"]
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
    


def stop_docker_compose(filepath=None):
    if filepath is None or filepath == "docker-compose.yml":
        filepath = os.path.join(BASE_DIR, "docker-compose.yml")
    elif not os.path.isabs(filepath):
        filepath = os.path.join(BASE_DIR, filepath)
    commands = [
        ["sudo", "aa-remove-unknown"],
        ["sudo", "systemctl", "restart", "docker"],
        ["sudo", "docker", "compose", "-f", filepath, "down"]
    ]

    for cmd in commands:
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            print(f"Command {' '.join(cmd)} completed with return code {process.returncode}")
            if stdout:
                print(stdout.decode())
            if stderr:
                print(stderr.decode())
        except Exception as e:
            print(f"Failed to run command {' '.join(cmd)}: {e}")