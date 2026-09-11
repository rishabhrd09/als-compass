#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [[ ! -f dist/index.html ]]; then
  echo 'Build first: bash scripts/build_pages.sh --preview' >&2
  exit 1
fi
export CLOUDFLARE_LOAD_DEV_VARS_FROM_DOT_ENV=false
export CLOUDFLARE_INCLUDE_PROCESS_ENV=false
export WRANGLER_SEND_METRICS=false
exec npx --yes wrangler@4.131.1 pages dev dist \
  --ip 127.0.0.1 --port "${CAREKOSH_PREVIEW_PORT:-8788}" \
  --compatibility-date=2026-09-11
