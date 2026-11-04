# part_assets.py: backend guide

Source: [src/part_assets.py](../../src/part_assets.py). [Documentation index](../README.md).

Build validated CPU rendering assets from JSON definitions or legacy OBJ content.

## How it works

`load_asset(path)` checks the first non-whitespace character to dispatch JSON versus OBJ. JSON goes through `load_part()`, including initial-position float32 precision checks, then uses box, sketch-prism, or feature-solid mesh generation. The returned `PartAsset` contains vertices and an optional `Part`.

Legacy OBJ parsing supports positive/negative indices and polygon fans, computes flat normals, and rejects malformed or non-finite geometry. It does not import materials/textures. Invalid JSON is never retried as OBJ.

## Contracts and editing considerations

- `vertices` is a flat `numpy.float32` array: `[x, y, z, nx, ny, nz, ...]`, three vertices per triangle. Positions are local metres.
- `box_vertices()` emits 36 vertices with analytic normals and checks that float32 dimensions remain noncollapsed.
- `PartAsset.color` yields normalized RGB from the part's hex color, or legacy gray `(0.72, 0.76, 0.82)`.
- Legacy assets have `part is None`; callers must handle missing material/domain data.
- No Qt/OpenGL context is required to load CPU geometry. Uploading it is a separate operation.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`PartAsset.color()`](../../src/part_assets.py#L16) | Resolve the part's hex color, or use the legacy mesh default. **Output:** tuple: Three RGB floats in the range 0 to 1. |
| [`loadObjFlatShaded(filename)`](../../src/part_assets.py#L27) | Read OBJ positions and faces, triangulate polygon fans, and compute flat normals. Supports negative indices but ignores material and texture sidecars. **Output:** numpy.ndarray: Flat float32 triangle data, six position/normal values per vertex; invalid meshes raise ValueError. |
| [`box_vertices(part)`](../../src/part_assets.py#L80) | Build a centered box mesh with analytic outward normals and check GPU precision. **Output:** numpy.ndarray: Flat float32 array for 36 vertices, each containing XYZ and normal XYZ. |
| [`load_asset(path)`](../../src/part_assets.py#L108) | Dispatch by file content to validated JSON geometry or legacy OBJ. Invalid JSON is never retried as OBJ; JSON spawn positions are checked for float32 precision. **Output:** PartAsset: CPU triangle mesh and optional Part definition; I/O and validation errors propagate. |

## Existing checks

[test_part_assets.py](../../Testing/Developer_Tests/test_part_assets.py), [test_obj_import.py](../../Testing/Developer_Tests/test_obj_import.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_format](part_format.md), [sketch_geometry](sketch_geometry.md), [feature_geometry](feature_geometry.md), [renderer](renderer.md), [scene](scene.md).
