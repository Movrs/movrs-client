# Gemini Project Guidelines

Before pushing any changes to the repository, please ensure you have updated the version number in `setup.py`. This is crucial for proper package versioning and deployment.

## Project Setup

### NVIDIA Docker Integration

- Added a script `movrs_client/setup_nvidia_docker.sh` to automate the setup of the NVIDIA Container Toolkit for Docker. This script now also installs `docker-compose`.
- The main application (`movrs_client/app.py`) now ensures this setup script is executed automatically on the first run.
- A flag file, `.setup_complete`, is created in the `movrs_client` directory after the setup to prevent the script from running again.
- The `.setup_complete` flag file has been added to `movrs_client/.gitignore`.
- Updated `movrs_client/movrs_apis.py` to use `docker-compose` instead of `docker compose`.
