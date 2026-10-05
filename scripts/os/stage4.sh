#!/usr/bin/env bash
# Stage 4 demo: ls, cd, du, cat, find on the multi-file VFS.
set -e
cd "$(dirname "$0")/../.."
bash run.sh --vfs vfs_examples/multiple_files.json --script scripts/emu/stage4.txt
