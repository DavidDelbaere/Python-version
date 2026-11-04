# simuO.py: backend guide

Source: [src/simuO.py](../../src/simuO.py). [Documentation index](../README.md).

The scene editor integration boundary for importing assets, persisting instances, resolving external part references, and deleting shared temporary assets.

This file serves both layers. See the [frontend companion](../Frontend/simuO.md) for its other responsibilities.

## How it works

`loadFile(path, uploadToGPU)` reads scene objects, resolves each part path, constructs/validates assets, then applies saved instance state. Asset loading completes before replacing the scene list. GPU replacement occurs afterward when requested; there is no complete rollback for arbitrary later GPU errors.

`saveFile()` collects permanent destinations for temporary imports before writing. It saves part copies and a version-1 scene, then updates in-memory paths and clears dirty state. `importFile()` validates/uploads before adding an instance. `deleteScenePart()` removes render resources and the instance, releasing a managed copy only after its last reference disappears.

## Contracts and editing considerations

- Scene records store name, meshPath, position, rotation, scale, velocity, restitution, body_type, acceleration, and angularVelocity. Geometry/material/metadata remain external.
- Saved instance values override part defaults when loading. Effective restitution/body type are serialized, so reopening makes them explicit overrides.
- Paths are made portable by `stored_mesh_path()` and recovered with `resolve_mesh_path()`.
- Each write is atomic individually; a group of scene/part writes is not transactional. Cancellation before destination collection finishes writes nothing.
- These are Qt-bound methods that may open dialogs and access GL resources, not headless service functions. Use format/document/asset helpers for backend-only work.
- `uploadToGPU=False` supports loading before the viewport initializes; subsequent GL initialization uploads the scene.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`SimuOMainWindow.loadFile(path, uploadToGPU=True)`](../../src/simuO.py#L252) | Load referenced assets and instance overrides before replacing scene objects; optionally rebuild GPU uploads. Parsing/asset errors propagate to the caller. **Output:** None. Updates project path, title, clean state, and camera framing for a single JSON part. |
| [`SimuOMainWindow.tryLoadFile(path, uploadToGPU=True)`](../../src/simuO.py#L359) | Attempt project loading, converting supported parse, schema, and filesystem errors into a warning dialog. **Output:** bool: True if loaded; False after displaying a load error. |
| [`SimuOMainWindow.importFile()`](../../src/simuO.py#L403) | Prompt for a part/OBJ, validate and upload it, then add it to the scene. OBJ imports become temporary copies after confirmation. **Output:** None. Marks successful imports dirty; errors release temporary copies and display a warning. |
| [`SimuOMainWindow.saveFile(checked=False, destination=None)`](../../src/simuO.py#L456) | Collect permanent temporary-part destinations and atomically write each part and scene reference file. Updates in-memory paths/clean state only after success; writes are not a multi-file transaction. **Output:** bool: True when saved; False on destination cancellation or reported filesystem failure. |
| [`SimuOMainWindow.saveAsFile()`](../../src/simuO.py#L568) | Prompt for a new scene path and delegate scene/temporary-part persistence to saveFile. **Output:** bool: True when saved; False on cancellation or failure. |
| [`SimuOMainWindow.deleteScenePart(sceneObject)`](../../src/simuO.py#L1142) | Remove one non-axis instance and its GPU resources; release a temporary copy only when no remaining object references it. **Output:** None. Marks dirty and refreshes temporary-part/status UI; unknown instances are ignored. |

## Existing checks

[test_project_safety.py](../../Testing/Developer_Tests/test_project_safety.py), [test_obj_import.py](../../Testing/Developer_Tests/test_obj_import.py), [test_properties.py](../../Testing/Developer_Tests/test_properties.py), [test_scene_deletion.py](../../Testing/Developer_Tests/test_scene_deletion.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[simuO](../Frontend/simuO.md), [scene](scene.md), [project_paths](project_paths.md), [temporary_parts](temporary_parts.md), [renderer](renderer.md).
