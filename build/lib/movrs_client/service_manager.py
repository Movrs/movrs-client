import subprocess
import os
import shutil
import tempfile

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
Environment="DISPLAY=:0"
Environment="QT_QPA_PLATFORM=xcb"
Type=forking
ExecStart=sudo docker-compose -f {docker_compose_path} up -d
ExecStop=sudo docker-compose -f {docker_compose_path} down
Restart=always

[Install]
WantedBy=multi-user.target
"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            tmp_file.write(service_content)
            tmp_file_path = tmp_file.name

        subprocess.run(["sudo", "mv", tmp_file_path, SERVICE_FILE_PATH], check=True)
        subprocess.run(["sudo", "chmod", "644", SERVICE_FILE_PATH], check=True)
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        return True
    except Exception as e:
        print(f"Error creating service file: {e}")
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
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
