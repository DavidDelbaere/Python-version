# feature_document.py: backend guide

Source: [src/feature_document.py](../../src/feature_document.py). [Documentation index](../README.md).

Persist current version-3 feature documents and migrate older editable JSON part definitions.

## How it works

`new_feature_document()` upgrades the default document envelope to version 3 and returns `(data, empty_model)`. `open_feature_document()` validates with drafts allowed, uses existing v3 history directly, or converts v1/v2 geometry into a Front-supported sketch. Closed older geometry gets a symmetric extrusion.

`save_feature_document()` builds the supplied model, copies document fields, writes current geometry/version, and atomically replaces the destination.

## Contracts and editing considerations

- Migration preserves metadata and material/physics fields. Version-2 points are shifted by the area centroid to retain their old rendered placement; box conversion uses centered rectangle coordinates.
- Opening a legacy OBJ file fails because it has no JSON editable history.
- Save returns the saved dictionary. It does not change the caller's document dictionary, though building refreshes the supplied model's derived data.
- Saving validates model geometry/name, not the complete material/physics schema. Use staged `load_part()`/`load_asset()` validation for backend edits to those fields.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`new_feature_document()`](../../src/feature_document.py#L13) | Create an empty version-3 part with default identity, material, and state. **Output:** tuple: Document dictionary and empty FeatureModel. |
| [`open_feature_document(path)`](../../src/feature_document.py#L24) | Load a JSON part, allowing drafts, and migrate older geometry to feature history. **Output:** tuple: Document dictionary and built FeatureModel; invalid files raise an error. |
| [`save_feature_document(path, data, model)`](../../src/feature_document.py#L54) | Rebuild the model and atomically save version-3 geometry in a copy of the document. Only geometry and name are checked here; use load_part for full schema validation. **Output:** dict: Saved document data; the input dictionary is not modified. |

## Existing checks

[test_feature_parts.py](../../Testing/Developer_Tests/test_feature_parts.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_document](part_document.md), [feature_geometry](feature_geometry.md), [feature_editor](feature_editor.md), [temporary_parts](temporary_parts.md).
