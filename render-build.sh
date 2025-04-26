#!/usr/bin/env bash
# This script runs during the build phase on Render.com

set -o errexit

echo "Starting custom build process for Twitch Auto-Farmer..."

# Install system dependencies (as root/sudo)
echo "Installing system dependencies..."
apt-get update
apt-get install -y wget gnupg2 unzip curl

# Install Chrome for Selenium
echo "Installing Chrome browser..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver matching Chrome version
echo "Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
CHROMEDRIVER_VERSION=$(wget -q -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Create persistent data directory for farming data
echo "Setting up data directory..."
mkdir -p /var/data
chmod -R 777 /var/data

# Environment setup for Poetry
echo "Setting up Poetry environment..."
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Show versions
echo "Environment details:"
echo "Python: $(python --version)"
echo "Chrome: $(google-chrome --version)"
echo "ChromeDriver: $(chromedriver --version)"
echo "Poetry: $(poetry --version)"

echo "Build script completed successfully!"