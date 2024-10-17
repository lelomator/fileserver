#!/bin/bash

# Exit on any error
set -e

# Update the system and install necessary packages
echo "Updating system and installing necessary packages..."
apt update
apt install -y git python3 python3-venv

# Navigate to the server directory
cd /mnt/server

# Clone the repository from GitHub
echo "Cloning the repository..."
git clone https://github.com/lelomator/fileserver.git .

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Ensure the upload directory exists
mkdir -p user-files

echo "Setup complete. Flask application is ready to be started!"
