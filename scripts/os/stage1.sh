#!/usr/bin/env bash
# Stage 1 demo: REPL, $VARIABLE expansion, error handling.
# The emulator reads the commands from the standard input.
set -e
cd "$(dirname "$0")/../.."
export DEMO_DIR=/home
bash run.sh < scripts/emu/stage1.txt
