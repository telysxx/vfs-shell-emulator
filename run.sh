#!/usr/bin/env bash
# Launch the emulator from any directory: bash run.sh [options]
cd "$(dirname "$0")" || exit 1
exec "${PYTHON:-python3}" src/main.py "$@"
