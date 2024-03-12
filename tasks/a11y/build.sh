pip3 install --no-cache-dir --upgrade scrapy chromedriver-autoinstaller
# node
apt update -y
apt install nodejs -y # Node 18.19 on last check
apt install npm --no-install-recommends -y

# axe + chrome + chromedriver
npm install @axe-core/cli -g

wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo 'deb [arch=arm64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google.list \
  && apt-get update \
  && apt-get install -y google-chrome-unstable --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

python -c "import chromedriver_autoinstaller;chromedriver_autoinstaller.install()"

mkdir results
