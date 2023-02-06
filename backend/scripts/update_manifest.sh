#!/bin/bash
set -e
SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
cd "${SCRIPT_DIR}/.."

env="${1:-dev}"  # dev or prod

echo -n "Create copilot/backend/manifest.yml ... "
jinja2 copilot/backend/manifest.template.yml \
    -D SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN}" \
    -D SLACK_USER_TOKEN="${SLACK_USER_TOKEN}" \
    -D SLACK_SIGNING_SECRET="${SLACK_SIGNING_SECRET}" \
    -D SLACK_BOT_TOKEN_DEV="${SLACK_BOT_TOKEN_DEV}" \
    -D SLACK_USER_TOKEN_DEV="${SLACK_USER_TOKEN_DEV}" \
    -D SLACK_SIGNING_SECRET_DEV="${SLACK_SIGNING_SECRET_DEV}" \
    -D OPENAI_ORGANIZATION="${OPENAI_ORGANIZATION}" \
    -D OPENAI_API_KEY="${OPENAI_API_KEY}" \
    > copilot/backend/manifest.yml
echo "Done"

echo -n "Create copilot/environments/${env}/manifest.yml ... "
jinja2 copilot/environments/${env}/manifest.template.yml \
    > copilot/environments/${env}/manifest.yml
echo "Done"
