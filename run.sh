#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${SIMUO_PYTHON:-$project_dir/.venv/bin/python}"

if [[ ! -x "$python_bin" ]]; then
    echo "SimuO's Python environment was not found: $python_bin" >&2
    echo "Follow the Linux Mint setup in README.md, or set SIMUO_PYTHON to a Python executable." >&2
    exit 1
fi

exec "$python_bin" "$project_dir/src/main.py" "$@"
