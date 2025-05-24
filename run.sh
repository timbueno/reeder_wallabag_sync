#!/bin/bash

# Exit on error
set -e

# Change to the directory of the script
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install package in development mode
echo "Installing package..."
pip install -e ".[dev]"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
FEED_URL=your_feed_url
WALLABAG_BASE_URL=your_wallabag_url
WALLABAG_CLIENT_ID=your_client_id
WALLABAG_CLIENT_SECRET=your_client_secret
WALLABAG_USERNAME=your_username
WALLABAG_PASSWORD=your_password
EOL
    echo "Please edit .env file with your configuration"
    exit 1
fi

# Run the script
echo "Running wallabag-sync..."
python -m wallabag_sync.cli

# Deactivate virtual environment
deactivate 