#!/usr/bin/env bash
# Stage 2 demo: every CLI parameter and the priority CLI > JSON.
set -e
cd "$(dirname "$0")/../.."
export DEMO_DIR=/home

echo "##### 1. Only CLI parameters"
bash run.sh --vfs vfs_examples/minimal.json --prompt "cli> " \
    --script scripts/emu/stage2.txt

echo "##### 2. Only the JSON file (config.json)"
bash run.sh --config config.json

echo "##### 3. CLI overrides the JSON file (prompt, vfs, script)"
bash run.sh --config config.json --prompt "override> " \
    --vfs vfs_examples/deep_tree.json --script scripts/emu/stage2.txt

echo "##### 4. Error: the config file does not exist"
bash run.sh --config no_such_config.json || echo "exit code: $?"

echo "##### 5. Error: the startup script does not exist"
bash run.sh --script no_such_script.txt || echo "exit code: $?"
