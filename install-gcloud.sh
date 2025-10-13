#!/bin/bash

# Google Cloud CLI Installation Script
# This script installs gcloud CLI system-wide using sudo

set -e  # Exit on any error

echo "🚀 Starting Google Cloud CLI installation..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Warning: Running as root. Consider running as a regular user with sudo."
fi

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "❌ curl is required but not installed. Please install curl first."
    echo "   Run: sudo apt update && sudo apt install curl"
    exit 1
fi

# Variables
GCLOUD_VERSION="455.0.0"
DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-${GCLOUD_VERSION}-linux-x86_64.tar.gz"
ARCHIVE_NAME="google-cloud-cli-${GCLOUD_VERSION}-linux-x86_64.tar.gz"
INSTALL_DIR="/opt/google-cloud-sdk"
BIN_DIR="/usr/local/bin"

echo "📥 Downloading Google Cloud CLI v${GCLOUD_VERSION}..."
curl -O "$DOWNLOAD_URL"

echo "📦 Extracting archive..."
tar -xzf "$ARCHIVE_NAME"

echo "🔧 Installing to system directory..."
sudo mv google-cloud-sdk "$INSTALL_DIR"

echo "⚙️  Running installation script..."
sudo "$INSTALL_DIR/install.sh" --quiet

echo "🔗 Creating system-wide symlinks..."
sudo ln -sf "$INSTALL_DIR/bin/gcloud" "$BIN_DIR/gcloud"
sudo ln -sf "$INSTALL_DIR/bin/gsutil" "$BIN_DIR/gsutil"
sudo ln -sf "$INSTALL_DIR/bin/bq" "$BIN_DIR/bq"

echo "🧹 Cleaning up download files..."
rm -f "$ARCHIVE_NAME"

echo "✅ Google Cloud CLI installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Run: gcloud auth login"
echo "   2. Run: gcloud config set project YOUR_PROJECT_ID"
echo "   3. Run: gcloud components update (optional)"
echo ""
echo "🔍 Verify installation:"
gcloud version

echo ""
echo "📍 Installation location: $INSTALL_DIR"
echo "🔗 Binaries linked to: $BIN_DIR"