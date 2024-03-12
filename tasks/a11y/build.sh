pip3 install --no-cache-dir --upgrade scrapy chromedriver-autoinstaller

# node
NODE_VERSION=v20.12.0
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
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google.list \
  && apt-get update \
  && apt-get install -y google-chrome-stable --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

python -c "import chromedriver_autoinstaller;chromedriver_autoinstaller.install()"
