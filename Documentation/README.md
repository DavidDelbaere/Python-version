# Developer documentation


## Reading paths

- **Scene editing:** frontend `main` → `startMenu` → `simuO` → `properties_dialog` / `renderer`.
- **Part authoring:** frontend `feature_editor` → `part_editor` / `part_viewport`; backend `sketch_geometry` → `feature_geometry` → `feature_document`.
- **Import/render:** backend `part_format` → `part_assets` → `scene` → `renderer`.
- **Persistence:** backend `simuO` → `project_paths` / `temporary_parts`; part files use `part_document` or `feature_document`.
- **Physics:** backend `physics_world` → frontend/backend `physics_render` → shared `renderer`.

For the end-to-end part architecture, see [SimuOPart](Backend/SimuOPart.md).

## Source file index

| Source file | Frontend guide | Backend guide |
| --- | --- | --- |
| [src/feature_document.py](../src/feature_document.py) | — | [Backend](Backend/feature_document.md) |
| [src/feature_editor.py](../src/feature_editor.py) | [Frontend](Frontend/feature_editor.md) | [Backend](Backend/feature_editor.md) |
| [src/feature_geometry.py](../src/feature_geometry.py) | — | [Backend](Backend/feature_geometry.md) |
| [src/main.py](../src/main.py) | [Frontend](Frontend/main.md) | — |
| [src/main.spec](../src/main.spec) | — | [Build instructions](../README.md#build-an-executable-optional) |
| [src/part_assets.py](../src/part_assets.py) | — | [Backend](Backend/part_assets.md) |
| [src/part_document.py](../src/part_document.py) | — | [Backend](Backend/part_document.md) |
| [src/part_editor.py](../src/part_editor.py) | [Frontend](Frontend/part_editor.md) | [Backend](Backend/part_editor.md) |
| [src/part_export.py](../src/part_export.py) | — | [Backend](Backend/part_export.md) |
| [src/part_format.py](../src/part_format.py) | — | [Backend](Backend/part_format.md) |
| [src/part_viewport.py](../src/part_viewport.py) | [Frontend](Frontend/part_viewport.md) | — |
| [src/physics_render.py](../src/physics_render.py) | [Frontend](Frontend/physics_render.md) | [Backend](Backend/physics_render.md) |
| [src/physics_world.py](../src/physics_world.py) | — | [Backend](Backend/physics_world.md) |
| [src/project_paths.py](../src/project_paths.py) | — | [Backend](Backend/project_paths.md) |
| [src/properties_dialog.py](../src/properties_dialog.py) | [Frontend](Frontend/properties_dialog.md) | — |
| [src/ray.py](../src/ray.py) | — | [Backend](Backend/ray.md) |
| [src/renderer.py](../src/renderer.py) | [Frontend](Frontend/renderer.md) | [Backend](Backend/renderer.md) |
| [src/resources.py](../src/resources.py) | — | [Backend](Backend/resources.md) |
| [src/scene.py](../src/scene.py) | — | [Backend](Backend/scene.md) |
| [src/simuO.py](../src/simuO.py) | [Frontend](Frontend/simuO.md) | [Backend](Backend/simuO.md) |
| [src/sketch_geometry.py](../src/sketch_geometry.py) | — | [Backend](Backend/sketch_geometry.md) |
| [src/startMenu.py](../src/startMenu.py) | [Frontend](Frontend/startMenu.md) | — |
| [src/temporary_parts.py](../src/temporary_parts.py) | — | [Backend](Backend/temporary_parts.md) |

## Shared data contracts

- Stored geometry/position use metres; mass uses kilograms; time uses seconds. Sketch and extrusion controls display millimetres.
- Scene Euler rotation uses degrees in `Rx * Ry * Rz` order; angular velocity uses radians per second. Scale is dimensionless.
- `Part` is a reusable validated definition. `PartAsset` holds CPU triangles. `SceneObject` holds instance transforms/motion and physics overrides. `.simuO` stores references and instance state; it does not embed part definitions.
- Render vertices are flat float32 position/normal values: six values per vertex, three vertices per triangle. CPU geometry rebuilds and GPU uploads are separate.
- File writes are atomic individually; saving multiple assets plus a scene is not a multi-file transaction.

## Current layout and commands

Application modules live together in `src`; existing flat imports resolve when launching `src/main.py`. Part/model files live in `Assets`, developer checks in `Testing/Developer_Tests`, and the independent experiment in `Testing/Part_Playground`. Developer scripts calculate the repository root from their current depth and write screenshots to the operating system's temporary directory.

Run commands from the repository root:

```bash
./Testing/Tools/run.sh --new
.venv/bin/python -m unittest discover -s Testing/Developer_Tests -v
.venv/bin/python -m unittest discover -s Testing/Part_Playground -v
.venv/bin/python -m PyInstaller --noconfirm src/main.spec
```

On Windows, use `Testing/Tools/run.bat` and `.venv\Scripts\python.exe`. Dependencies, including PyInstaller, are declared in the root `requirements.txt`. `src/main.spec` is the only build specification; VS Code and Windows CI use that path. Launchers in `Testing/Tools` locate the repository two levels above themselves and resolve the interpreter and entry point from there, while user-supplied project arguments remain relative to the caller's working directory.

If you move source modules into packages later, update the Python imports, this index, tests, and build configuration together. Virtual environments contain absolute activation/script paths; recreate `.venv` after relocating the checkout if those environment commands stop working. The documented `python -m pip` commands avoid relying on a relocated `pip` script.

Copied virtual environments, caches, editor swap files, and generated binaries are excluded from this source index.
