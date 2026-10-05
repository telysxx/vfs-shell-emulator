#!/usr/bin/env bash
# Stage 3 demo: minimal VFS, several files, three levels, all commands.
set -e
cd "$(dirname "$0")/../.."

echo "##### Minimal VFS"
bash run.sh --vfs vfs_examples/minimal.json --script scripts/emu/stage3_minimal.txt

echo "##### Several files"
bash run.sh --vfs vfs_examples/multiple_files.json \
    --script scripts/emu/stage3_files.txt

echo "##### Three and more levels"
bash run.sh --vfs vfs_examples/deep_tree.json --script scripts/emu/stage3_deep.txt

echo "##### All commands of stages 1-3 with errors"
bash run.sh --vfs vfs_examples/multiple_files.json \
    --script scripts/emu/stage3_all.txt

echo "##### Error: broken VFS file"
bash run.sh --vfs README.md || echo "exit code: $?"
