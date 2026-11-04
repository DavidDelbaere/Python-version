# main.spec: backend guide

Source: [src/main.spec](../../src/main.spec). [Documentation index](../README.md).

The PyInstaller build recipe stored under `src`, collecting the desktop application and shipped resources into an executable.

## How it works

This is a build-time Python specification, not an application module. `project_root` is calculated from `SPECPATH` (the directory containing the specification), then `Analysis` targets repository `src/main.py` with `src` on its search path.

The recipe includes `Images`, `Assets`, and CustomTkinter data, creates a PYZ archive, and constructs the windowed `SimuO` executable with `EXE`. It has no function declarations.

## Contracts and editing considerations

- This is the single build specification. From the repository root, run `.venv/bin/python -m PyInstaller --noconfirm src/main.spec`; VS Code and Windows CI use the same path.
- Source package imports must resolve before PyInstaller can analyze them. Merely moving files into subfolders does not make old flat imports valid.
- `PIL._imagingtk` and `PIL._tkinter_finder` are explicit hidden imports: Pillow loads its Tk locator from a compiled extension when the startup logo becomes a Tk photo. A `--help` smoke check alone does not exercise this path. Other dynamic modules may also need explicit collection if analysis cannot discover them.
- Build on the target operating system. Generated executables require working desktop graphics support for rendering.
- Application and build dependencies, including PyInstaller, are declared together in the root `requirements.txt`. Install them with the environment interpreter using `-m pip install -r requirements.txt`.

## Related documentation

[main](../Frontend/main.md), [resources](resources.md), [renderer](renderer.md).

## Packaged startup check

On Linux with an X11/XWayland desktop and `wmctrl`, exercise the actual startup window and Pillow logo path after building:

```bash
.venv/bin/python Testing/Developer_Tests/gui_packaged_startup.py dist/SimuO
```

The check starts the executable from a temporary working directory, waits for its new startup window, closes that window, and requires a clean exit. This catches dynamically imported image/Tk dependencies that `--help` does not load.
