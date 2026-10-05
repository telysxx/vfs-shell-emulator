#!/usr/bin/env bash
# Stage 1 demo: REPL, $VARIABLE expansion, error handling.
set -e
cd "$(dirname "$0")/../.."
export DEMO_DIR=/home
bash run.sh --vfs vfs_examples/minimal.json --script scripts/emu/stage1.txt
