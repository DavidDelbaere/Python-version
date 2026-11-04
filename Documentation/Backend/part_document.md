# part_document.py: backend guide

Source: [src/part_document.py](../../src/part_document.py). [Documentation index](../README.md).

Create, open, and atomically save the older version-2 editable sketch document representation.

## How it works

`new_document()` supplies a UUID, SI units, default material/physics, spawn state, and empty sketch. `open_document()` calls `load_part(..., allow_draft=True)` and returns `(data, sketch)`; non-sketch parts are represented by a rectangle from their bounds. The current feature editor uses `feature_document.py` for richer migration.

`save_document(path, data, sketch)` validates the sketch, writes copied data with version-2 geometry, and returns the saved dictionary without modifying the original dictionary.

## Contracts and editing considerations

- Open outlines can be saved as drafts but cannot be imported as scene solids.
- Saving checks geometry, a nonempty name, and finite JSON encoding; it does not fully revalidate other material/physics fields.
- Backend changes to nongeometry fields should validate a staged file through `load_part()` or `load_asset()` before replacement.
- Atomic replacement is per file and requires an existing writable parent directory.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`new_document()`](../../src/part_document.py#L12) | Create a version-2 draft with a new UUID and default material and physics settings. **Output:** dict: New document with an empty sketch and SI units. |
| [`open_document(path)`](../../src/part_document.py#L27) | Load an editable sketch document, allowing drafts; otherwise use the part bounds to make a rectangular sketch. **Output:** tuple: Document dictionary and independent Sketch, represented as version 2. |
| [`save_document(path, data, sketch)`](../../src/part_document.py#L49) | Validate the sketch and atomically save version-2 geometry in a document copy. Other material and physics fields are not fully revalidated here. **Output:** dict: Saved document data; validation or filesystem failures propagate. |

## Existing checks

[test_sketch_parts.py](../../Testing/Developer_Tests/test_sketch_parts.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[feature_document](feature_document.md), [part_format](part_format.md), [temporary_parts](temporary_parts.md), [part_editor](../Frontend/part_editor.md).
