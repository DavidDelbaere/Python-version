# SimuO OpenGL Renderer

## Setup and run

The pinned Qt dependency supports **CPython 3.10–3.14**.
A graphics driver supporting **OpenGL 3.3 Core** is required.

Run your OS's commands below from the project root. Confirm the first command
reports Python 3.10–3.14 before continuing.

### Windows (PowerShell)

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python tools/check_setup.py --graphics
python main.py
```

### macOS (Terminal)

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
bash tools/check_setup.sh --graphics
python main.py
```

### Linux (Bash)

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/check_setup.py --graphics
python main.py
```

If your default Python is outside the supported range, select an installed
supported version instead, such as `py -3.12` on Windows or `python3.12` on
macOS/Linux, for the version check and environment creation.

The setup check briefly opens a window to test rendering; omit `--graphics` for
environment checks only. In a new terminal, activate `.venv` again before running
`python main.py`.

## Tests

```text
python -m unittest discover -s tests -t . -v
```

Rendering tests require a desktop OpenGL display.

## Guides

- [Controls and editor panels](docs/controls.md)
- [Project structure, development, and troubleshooting](docs/development.md)
