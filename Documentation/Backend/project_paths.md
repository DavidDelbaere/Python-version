# project_paths.py: backend guide

Source: [src/project_paths.py](../../src/project_paths.py). [Documentation index](../README.md).

Convert between saved scene mesh references and actual model files while supporting portable projects and older Windows paths.

## How it works

`resolve_mesh_path(value, project_path)` normalizes separators, tries a native absolute path or project-relative path, then checks beside the scene, its `Assets` directory, and bundled assets. It returns a resolved existing `Path`, or raises `FileNotFoundError`.

`stored_mesh_path(mesh_path, project_path)` returns a POSIX-style relative reference. If Windows drives make that impossible, it stores an absolute path.

## Contracts and editing considerations

- Model bytes are external to `.simuO` scenes. Keep referenced parts with the project when moving it.
- Recovery by filename can resolve a different same-named asset; use intentional project layouts.
- These helpers do not create, parse, or validate mesh contents.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`resolve_mesh_path(value, project_path)`](../../src/project_paths.py#L9) | Resolve a saved mesh reference, recovering legacy Windows paths beside the project or in project/bundled Assets folders. **Output:** pathlib.Path: Resolved existing model; raises FileNotFoundError if no candidate exists. |
| [`stored_mesh_path(mesh_path, project_path)`](../../src/project_paths.py#L47) | Express a model path relative to its scene for portable persistence. **Output:** str: POSIX-style relative path, or an absolute path when Windows drives differ. |

## Existing checks

[test_portability.py](../../Testing/Developer_Tests/test_portability.py), [test_project_safety.py](../../Testing/Developer_Tests/test_project_safety.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[resources](resources.md), [simuO](simuO.md), [temporary_parts](temporary_parts.md).
