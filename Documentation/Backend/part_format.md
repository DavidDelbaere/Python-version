# part_format.py: backend guide

Source: [src/part_format.py](../../src/part_format.py). [Documentation index](../README.md).

The authoritative JSON `.simuOPart` validator and renderer-independent `Part` domain object.

## How it works

`load_part(path, allow_draft=False)` reads UTF-8/BOM JSON, rejects duplicate keys and non-finite constants, validates the field contract, constructs geometry, and derives mass/inertia checks. It returns a frozen `Part` definition. File errors propagate; invalid definitions raise `ValueError`.

Version 1 is a box; version 2 is an editable sketch/prism; version 3 is ordered sketch/extrusion history. `allow_draft=True` permits unfinished geometry for document editors; normal asset import requires a solid.

## Contracts and editing considerations

- Units are metres, kilograms, and seconds; coordinates are right-handed with +Y up.
- Required top-level fields are format/version, identity, units/coordinates, geometry, appearance, material, physics, and initial state. Description and namespaced custom properties are optional.
- Density is positive; friction is nonnegative; restitution is in [0, 1]. Static definitions require zero initial velocity.
- Density-derived mass excludes an explicit mass field. Explicit mass requires one. Solid mass must be positive and finite.
- `Part.volume` follows actual supported geometry. `Part.inertia` uses the bounding-box diagonal formula, exact for boxes and approximate for other shapes.
- `Part.vertices(position)` returns translated geometry positions without normals, rotation, or scaling; it is not the GPU vertex buffer.
- A frozen dataclass does not deeply freeze nested geometry/metadata. Reload validated document data rather than mutating nested values as an update API.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`number(value, label, minimum=None, maximum=None)`](../../src/part_format.py#L9) | Validate a finite numeric scalar, excluding booleans, against optional inclusive bounds. **Output:** float: Converted value; raises ValueError for invalid numbers or bounds violations. |
| [`vector(value, label, positive=False)`](../../src/part_format.py#L36) | Validate a JSON three-component numeric list, optionally requiring positive components. **Output:** tuple: Three finite floats; raises ValueError for invalid input. |
| [`fields(value, label, required, optional=())`](../../src/part_format.py#L56) | Check that a JSON object contains all required keys and no unsupported keys. **Output:** dict: The original object, without copying; raises ValueError for a schema mismatch. |
| [`string(value, label)`](../../src/part_format.py#L78) | Validate that a value is a nonempty string after whitespace checking. **Output:** str: Original string, preserving whitespace; raises ValueError if invalid. |
| [`Part.volume()`](../../src/part_format.py#L112) | Calculate unscaled volume from box dimensions, sketch area and thickness, or the feature union. **Output:** float: Volume in cubic metres; draft geometry can have zero volume. |
| [`Part.inertia()`](../../src/part_format.py#L126) | Estimate diagonal inertia with the bounding-box formula, exact for a uniform box and approximate for other geometry. **Output:** tuple: Ixx, Iyy, Izz in kg m² using the part's unscaled dimensions and mass. |
| [`Part.vertices(position)`](../../src/part_format.py#L136) | Translate geometry points by a supplied position without rotation or scaling. **Output:** list: XYZ tuples in metres; box corners, sketch cap points, or feature mesh positions, without normals. |
| [`load_part(path, allow_draft=False)`](../../src/part_format.py#L161) | Parse and validate an SI JSON part, including geometry, material, derived mass, and initial state. Custom properties are inert metadata. **Output:** Part: Validated frozen definition; malformed data raises ValueError and file errors propagate. |
| [`load_part.unique_pairs(pairs)`](../../src/part_format.py#L174) | Build a decoded JSON object while rejecting duplicate keys. **Output:** dict: Object made from the supplied pairs; duplicates raise ValueError. |
| [`load_part.invalid_constant(value)`](../../src/part_format.py#L190) | Reject the JSON parser's non-finite constants such as NaN or Infinity. **Output:** No return value: Always raises ValueError. |

## Existing checks

[test_part_assets.py](../../Testing/Developer_Tests/test_part_assets.py), [test_sketch_parts.py](../../Testing/Developer_Tests/test_sketch_parts.py), [test_feature_parts.py](../../Testing/Developer_Tests/test_feature_parts.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[part_assets](part_assets.md), [sketch_geometry](sketch_geometry.md), [feature_geometry](feature_geometry.md), [scene](scene.md), [SimuOPart](SimuOPart.md).
