import json
from movrs_client.movrs_apis import (
    get_user_data,
    read_json_file,
    BASEURL,
    update_json_fields,
    image_exists_locally,
)
import subprocess
import yaml
import os
import requests
import shutil

# Determine the base directory of the installed package
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE DIR", BASE_DIR)


def check_version_to_update():
    data = read_json_file(os.path.join(BASE_DIR, "user_cred.json"))
    user_data = get_user_data(data.get("logged_user_id"))[0]
    return user_data["version_id"]


def is_docker_installed_with_sudo():
    try:
        result = subprocess.run(
            ["sudo", "docker", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,  # automatically decodes output
        )
        print("Docker is installed and accessible with sudo:", result.stdout.strip())
        return True
    except FileNotFoundError:
        print("Docker or sudo not found.")
        return False
    except subprocess.CalledProcessError as e:
        print("Docker command failed with sudo:", e.stderr.strip())
        return False


def find_gcloud():
    # 1. Check PATH
    gcloud_path = shutil.which("gcloud")
    print("GCLOUD Path: ", gcloud_path)
    if gcloud_path:
        return gcloud_path

    # 2. Check common locations
    common_paths = [
        "/usr/local/google/cloud/sdk/bin/gcloud",
        os.path.expanduser("~/google-cloud-sdk/bin/gcloud"),
        "/snap/bin/gcloud",
        "/usr/bin/gcloud",
        "/usr/local/bin/gcloud",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    return None


def authenticate_docker_with_service_account(json_key_path):
    gcloud_executable = find_gcloud()
    if not gcloud_executable:
        print("❌ 'gcloud' command not found.")
        print(
            "Please install the Google Cloud SDK and ensure 'gcloud' is in your PATH or in a standard location."
        )
        print("Installation instructions: https://cloud.google.com/sdk/docs/install")
        raise FileNotFoundError(
            "'gcloud' command not found. Please install the Google Cloud SDK."
        )
    try:
        print("🔐 Authenticating Docker with service account...")
        subprocess.run(
            [
                gcloud_executable,
                "auth",
                "activate-service-account",
                "--key-file",
                json_key_path,
            ],
            check=True,
        )
        subprocess.run(
            [
                gcloud_executable,
                "auth",
                "configure-docker",
                "us-central1-docker.pkg.dev",
            ],
            check=True,
        )
        print("✅ Docker configured for authentication.")
    except subprocess.CalledProcessError as e:
        print("❌ Authentication failed:", e)


def pull_image_with_sudo(image_name):
    try:
        print(f"⬇️ Pulling image with sudo: {image_name}")
        subprocess.run(["docker", "pull", image_name], check=True)
        print("✅ Image pulled successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to pull image:", e)


def install_docker():
    try:
        print("🚀 Installing Docker...")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(
            [
                "sudo",
                "apt-get",
                "install",
                "-y",
                "ca-certificates",
                "curl",
                "gnupg",
                "lsb-release",
            ],
            check=True,
        )

        subprocess.run(["sudo", "mkdir", "-p", "/etc/apt/keyrings"], check=True)

        subprocess.run(
            [
                "curl",
                "-fsSL",
                "https://download.docker.com/linux/ubuntu/gpg",
                "|",
                "sudo",
                "gpg",
                "--dearmor",
                "-o",
                "/etc/apt/keyrings/docker.gpg",
            ],
            shell=True,
            check=True,
        )

        subprocess.run(
            [
                "echo",
                """"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] """
                '''https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"''',
                "|",
                "sudo",
                "tee",
                "/etc/apt/sources.list.d/docker.list",
                ">",
                "/dev/null",
            ],
            shell=True,
            check=True,
        )

        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(
            [
                "sudo",
                "apt-get",
                "install",
                "-y",
                "docker-ce",
                "docker-ce-cli",
                "containerd.io",
                "docker-buildx-plugin",
                "docker-compose-plugin",
            ],
            check=True,
        )
        print("✅ Docker installed successfully.")

    except subprocess.CalledProcessError as e:
        print("❌ Docker installation failed:", e)


def get_version_details():
    url = BASEURL + "/version/get-data"

    response = requests.post(url)
    response_data = response.json()
    return response_data


def update_to_version(new_version):
    print(f"Updating to version {new_version}")
    data = read_json_file(os.path.join(BASE_DIR, "current_state.json"))
    current_version = data.get("current_version")

    version_details = get_version_details()
    version_data = version_details["result_data"]
    version_to_find = new_version

    filtered = next(
        (item for item in version_data if item["version_id"] == version_to_find), None
    )

    if not filtered:
        print(f"Version {new_version} not found.")
        return f"Version {new_version} not found"

    docker_images = filtered["docker_images"]

    missing_images = [
        img for img in docker_images.values() if not image_exists_locally(img)
    ]

    if new_version == current_version and not missing_images:
        return "Version is up to date"

    print("filtered", filtered)
    print("docker_images", docker_images)

    if missing_images:
        print("Missing images found, pulling...", missing_images)

    result = is_docker_installed_with_sudo()
    if not result:
        install_docker()

    json_key_path = os.path.join(BASE_DIR, "movrs-read.json")
    print("JSON KEY Present: ", json_key_path)
    authenticate_docker_with_service_account(json_key_path)
    update_docker_compose_file(
        os.path.join(BASE_DIR, "docker-compose.yml"), docker_images
    )
    for key, value in docker_images.items():
        if value in missing_images:
            pull_image_with_sudo(value)
        else:
            print(f"Image {value} already exists locally.")

    update_json_fields(
        [["current_version", new_version]],
        os.path.join(BASE_DIR, "current_state.json"),
    )
    print(new_version, "current_version", current_version)
    return "Version updated"


def confirm_version_check():
    new_version = check_version_to_update()
    return update_to_version(new_version)


def create_env(user_home):
    env_file = ".env"
    # Check if USER_HOME is already set
    if "USER_HOME" not in os.environ:
        print(f"USER_HOME not found. Setting it to {user_home}.")
        os.environ["USER_HOME"] = user_home

        # Append to .env if not already present
        if not os.path.exists(env_file):
            with open(env_file, "w") as f:
                f.write(f"USER_HOME={user_home}\n")
        else:
            with open(env_file, "r") as f:
                lines = f.readlines()
            if not any(line.startswith("USER_HOME=") for line in lines):
                with open(env_file, "a") as f:
                    f.write(f"USER_HOME={user_home}\n")
        print(f"{user_home} added to environment and .env file.")
    else:
        print(f"USER_HOME is already set to {os.environ['USER_HOME']}.")


def update_docker_compose_file(file_path: str, docker_images: dict):
    # Match service name to docker_images key
    service_to_image_key = {
        "backend": "movrs_backend",
        "frontend": "movrs_ui",
        "magic_motion": "movrs_magic_motion",
    }

    # Load existing YAML
    with open(file_path, "r") as f:
        compose_data = yaml.safe_load(f)
    home_directory = os.path.expanduser("~")

    create_env(home_directory)

    # Update image tags
    for service, image_key in service_to_image_key.items():
        if service in compose_data["services"] and image_key in docker_images:
            compose_data["services"][service]["image"] = docker_images[image_key]

    # Write back to the same file
    with open(file_path, "w") as f:
        yaml.dump(compose_data, f, sort_keys=False)
