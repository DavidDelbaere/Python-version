#!/usr/bin/env bash
# Launch the source app using the environment at the repository root.
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
python_bin="${SIMUO_PYTHON:-$project_dir/.venv/bin/python}"

if [[ ! -x "$python_bin" ]]; then
    echo "SimuO's Python environment was not found: $python_bin" >&2
    echo "Follow the setup in $project_dir/README.md, or set SIMUO_PYTHON to a Python executable." >&2
    exit 1
fi

exec "$python_bin" "$project_dir/src/main.py" "$@"
