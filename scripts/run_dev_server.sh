#!/bin/bash
set -e
SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
cd "${SCRIPT_DIR}/.."

SLACK_BOT_TOKEN="${SLACK_BOT_TOKEN_DEV}" \
SLACK_USER_TOKEN="${SLACK_USER_TOKEN_DEV}" \
SLACK_SIGNING_SECRET="${SLACK_SIGNING_SECRET_DEV}" \
uvicorn app.app:app --host 0.0.0.0 --port 8080 --reload --log-level debug
