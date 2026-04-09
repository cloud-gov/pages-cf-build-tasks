#!/usr/bin/env bash

mkdir /zap/wrk

NODE_VERSION=v24.14.1
wget "https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz" \
  && mkdir -p /usr/local/lib/nodejs \
  && tar -xJvf node-${NODE_VERSION}-linux-x64.tar.xz -C /usr/local/lib/nodejs \
  && ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/node /usr/bin/node \
  && ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/npm /usr/bin/npm \
  && ln -s /usr/local/lib/nodejs/node-${NODE_VERSION}-linux-x64/bin/npx /usr/bin/npx \
  && rm -f "node-${NODE_VERSION}-linux-x64.tar.xz"

# reporter dependencies
npm --prefix build-task/reporter/ install
