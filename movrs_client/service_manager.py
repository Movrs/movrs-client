import subprocess
import os
import shutil

# Determine the base directory of the installed package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_NAME = "movrs.service"
SERVICE_FILE_PATH = os.path.join("/etc/systemd/system", SERVICE_NAME)

def create_service_file():
    docker_compose_path = os.path.join(BASE_DIR, "docker-compose.yml")
    docker_path = shutil.which('docker')

    if not docker_path:
        print("Error: 'docker' executable not found in PATH.")
        return False

    service_content = f"""[Unit]
Description=MOVRS Client Service
After=network.target

[Service]
User=root
Group=root
Type=forking
ExecStart=sudo docker-compose -f {docker_compose_path} up -d
ExecStop=sudo docker-compose -f {docker_compose_path} down
Restart=always

[Install]
WantedBy=multi-user.target
"""
    try:
        with open(SERVICE_FILE_PATH, "w") as f:
            f.write(service_content)
        
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        return True
    except Exception as e:
        print(f"Error creating service file: {e}")
        return False

def enable_service():
    try:
        subprocess.run(["sudo", "systemctl", "enable", SERVICE_NAME], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error enabling service: {e}")
        return False

def start_service():
    try:
        subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error starting service: {e}")
        return False

def stop_service():
    try:
        subprocess.run(["sudo", "systemctl", "stop", SERVICE_NAME], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error stopping service: {e}")
        return False

def disable_service():
    try:
        subprocess.run(["sudo", "systemctl", "disable", SERVICE_NAME], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error disabling service: {e}")
        return False
