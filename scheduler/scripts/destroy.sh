#!/bin/bash
set -e
SCRIPT_DIR="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
cd "${SCRIPT_DIR}/../app"

stage="${1:-dev}"  # dev or prod

chalice delete --stage ${stage}
