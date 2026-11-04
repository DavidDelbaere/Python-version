# part_export.py: backend guide

Source: [src/part_export.py](../../src/part_export.py). [Documentation index](../README.md).

Export local solid mesh geometry to OBJ or ASCII STL while retaining the editable document separately.

## How it works

`export_sketch(path, sketch, kind)` requires a closed sketch, generates its prism, and delegates to `export_vertices()`. `export_vertices(path, vertices, kind)` reshapes interleaved geometry into triangles, writes OBJ positions/face normals or ASCII STL facets, then atomically replaces the file.

## Contracts and editing considerations

- `kind` is `obj` or `stl`. Both formats use local metres; STL has no embedded unit field.
- Input vertices contain XYZ plus normal XYZ, reshapeable to `(triangle_count, 3, 6)`.
- Exports do not contain scene transforms, editable features/dimensions, physical materials, or custom metadata.
- Empty geometry and unsupported formats raise `ValueError`; STL also rejects degenerate triangles. Filesystem errors propagate.
- Export helpers do not update editor path, dirty state, or undo history.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`export_sketch(path, sketch, kind)`](../../src/part_export.py#L8) | Build a closed sketch's local prism mesh and atomically export it without modifying the document. **Output:** None. Writes OBJ or ASCII STL in metres; invalid geometry/format raises ValueError and I/O errors propagate. |
| [`export_vertices(path, vertices, kind)`](../../src/part_export.py#L29) | Atomically export local triangle geometry to OBJ or ASCII STL. Editable history, physics, and scene transforms are not included; STL carries no units. **Output:** None. Writes the destination; an empty mesh, invalid format, or degenerate STL triangle raises ValueError. |

## Existing checks

[test_part_exports.py](../../Testing/Developer_Tests/test_part_exports.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[sketch_geometry](sketch_geometry.md), [feature_geometry](feature_geometry.md), [temporary_parts](temporary_parts.md), [part_editor](../Frontend/part_editor.md), [feature_editor](../Frontend/feature_editor.md).
