#!/bin/bash
set -e
SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
cd "${SCRIPT_DIR}/../app"

stage="${1:-dev}"  # dev or prod

poetry export -f requirements.txt --output requirements.txt --only main
jinja2 .chalice/config.template.json \
    -D APPRUNNER_ARN="${APPRUNNER_ARN}" \
    -D APPRUNNER_ARN_DEV="${APPRUNNER_ARN_DEV}" \
    > .chalice/config.json

chalice deploy --stage ${stage}
