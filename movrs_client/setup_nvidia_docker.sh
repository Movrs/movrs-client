#!/bin/bash

set -e

echo "️ Setting up NVIDIA Container Toolkit for Docker..."

# 1. Update and install dependencies
echo " Installing dependencies..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. Add NVIDIA GPG key
echo " Adding NVIDIA GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /etc/apt/keyrings/nvidia-container-toolkit.gpg

# 3. Add NVIDIA Container Toolkit repository
echo " Adding NVIDIA repository..."
distribution=$(. /etc/os-release; echo "$ID$VERSION_ID")
curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" | \
  sed 's#deb https://#deb [signed-by=/etc/apt/keyrings/nvidia-container-toolkit.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null

# 4. Install NVIDIA Container Toolkit
echo " Installing NVIDIA Container Toolkit..."
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo apt-get install -y docker-compose

# 5. Configure Docker daemon to use NVIDIA runtime
echo "️ Configuring Docker daemon for NVIDIA runtime..."

DOCKER_DAEMON_FILE="/etc/docker/daemon.json"
if [ -f "$DOCKER_DAEMON_FILE" ]; then
    sudo cp "$DOCKER_DAEMON_FILE" "$DOCKER_DAEMON_FILE.bak"
    echo " Backed up existing daemon.json to daemon.json.bak"
fi

sudo bash -c "cat > $DOCKER_DAEMON_FILE" <<EOF
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
EOF

# 6. Restart Docker
echo " Restarting Docker..."
sudo systemctl restart docker

# 7. Verify
echo "✅ Setup complete. Verifying NVIDIA runtime is available..."
docker info | grep -i 'runtimes'

echo " Try running: docker run --rm --runtime=nvidia nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi"

