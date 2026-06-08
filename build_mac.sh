#!/usr/bin/env bash
set -euo pipefail

pyinstaller \
  --onefile \
  --windowed \
  --name "TeamsKeepAlive" \
  --osx-bundle-identifier com.keepalive.teams \
  main.py

echo "Built: dist/TeamsKeepAlive"
