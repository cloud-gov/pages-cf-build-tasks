#!/usr/bin/env bash

pip3 install --no-cache-dir --upgrade scrapy

# get that wget and gnupg to install the deps
apt update && apt install gnupg wget -y

# node
NODE_VERSION=v24.14.1
wget "https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz" \
  && mkdir -p /usr/local/lib/nodejs \
  && tar -xJvf node-${NODE_VERSION}-linux-x64.tar.xz -C /usr/local/lib/nodejs \
  && ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/node /usr/bin/node \
  && ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/npm /usr/bin/npm \
  && ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/npx /usr/bin/npx \
  && rm -f "node-${NODE_VERSION}-linux-x64.tar.xz"

# axe
npm install @axe-core/cli -g
ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/axe /usr/bin/axe

# reporter dependencies
npm --prefix build-task/reporter/ install

# chrome + chromedriver
# Install dependencies for Chrome installation
apt install -y unzip jq curl

# Install Chrome dependencies
# These are the shared libraries required by Chrome binary
apt install -y \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libpango-1.0-0 \
  libcairo2 \
  libasound2 \
  libatspi2.0-0 \
  --no-install-recommends

# Fetch the latest stable Chrome and ChromeDriver versions from Chrome for Testing
CHROME_DATA=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json")
CHROME_VERSION=$(echo "$CHROME_DATA" | jq -r '.channels.Stable.version')
CHROME_URL=$(echo "$CHROME_DATA" | jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64") | .url')
CHROMEDRIVER_URL=$(echo "$CHROME_DATA" | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url')

echo "Installing Chrome and ChromeDriver version: $CHROME_VERSION"

# Download and install Chrome
wget -q "$CHROME_URL" -O /tmp/chrome-linux64.zip \
  && unzip -o /tmp/chrome-linux64.zip -d /opt/google \
  && ln -sf /opt/google/chrome-linux64/chrome /usr/bin/google-chrome \
  && rm /tmp/chrome-linux64.zip

# Download and install matching ChromeDriver
wget -q "$CHROMEDRIVER_URL" -O /tmp/chromedriver-linux64.zip \
  && unzip -o /tmp/chromedriver-linux64.zip -d /tmp/ \
  && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
  && chmod +x /usr/local/bin/chromedriver \
  && rm -rf /tmp/chromedriver*

# Verify installation
echo "Chrome installed: $(google-chrome --version)"
echo "ChromeDriver installed: $(chromedriver --version)"
