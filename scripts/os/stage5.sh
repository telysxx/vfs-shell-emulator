#!/usr/bin/env bash
# Stage 5 demo: rmdir and cp (changes live only in memory).
set -e
cd "$(dirname "$0")/../.."
bash run.sh --vfs vfs_examples/multiple_files.json --script scripts/emu/stage5.txt
