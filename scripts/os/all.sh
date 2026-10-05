#!/usr/bin/env bash
# Run the demos of all stages one after another.
set -e
cd "$(dirname "$0")"
for stage in stage1 stage2 stage3 stage4 stage5; do
    echo "=============== ${stage} ==============="
    bash "${stage}".sh
done
