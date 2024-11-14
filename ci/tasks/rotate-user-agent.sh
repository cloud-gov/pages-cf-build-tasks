#!/bin/bash

set -e

export CREDHUB_CA_CERT='master-bosh.crt'
echo "$CREDHUB_CA_CERT_VALUE" > $CREDHUB_CA_CERT

credhub api --server "$CREDHUB_SERVER"

cf api $CF_API
cf auth

cf t -o $CF_ORG -s $CF_SPACE

# for an explanation of this script, see:
# https://github.com/cloud-gov/internal-docs/blob/main/docs/runbooks/AWS/waf-pages-string-rotation.md

cf update-user-provided-service user-agent -p "{ \"USER_AGENT\": \"$USER_AGENT_NEW\" }"
credhub set \
    --name /concourse/pages/cf-build-tasks/com-waf-search-string-pages-slot-1  \
    --type value \
    --value "$USER_AGENT_NEW"

credhub regenerate --name /concourse/pages/cf-build-tasks/com-waf-search-string-pages-slot-2
