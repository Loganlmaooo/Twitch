#!/usr/bin/env bash
# This script runs during the build phase on Render.com

set -o errexit

# Install Chrome and dependencies for Selenium
apt-get update
apt-get install -y wget gnupg2 unzip

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Install Chromedriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
CHROMEDRIVER_VERSION=$(wget -q -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Create data directory
mkdir -p /var/data
chmod -R 777 /var/data

echo "Build script complete!"