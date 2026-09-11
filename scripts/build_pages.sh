#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
export CAREKOSH_STATIC_BUILD=1
python3 -m pip install --disable-pip-version-check -r requirements-static.txt
python3 scripts/build_static.py "$@"
