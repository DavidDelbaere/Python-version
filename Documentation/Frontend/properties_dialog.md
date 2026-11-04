# properties_dialog.py: frontend guide

Source: [src/properties_dialog.py](../../src/properties_dialog.py). [Documentation index](../README.md).

A modal UI for editing one scene instance's dynamic/static state, bounce, and initial linear velocity.

## How it works

Construction reads effective `SceneObject` values into controls but does not mutate the object. `values()` returns `(bounce, velocity)` after interaction; the owner separately reads the Dynamic body checkbox. `SimuOMainWindow.openPropertiesDialog()` applies accepted values and handles dirty-state/repaint bookkeeping.

## Contracts and editing considerations

- Bounce ranges from 0 to 1. Velocity components display m/s. These are instance settings saved in `.simuO`, not edits to the part definition.
- Untouched controls return original values, preserving precision beyond displayed decimals. Change tracking distinguishes an untouched control from an edited one.
- Cancel has no state effect. Existing playback windows use earlier snapshots; start a new Render window for edited properties.
- Legacy and sketch/feature mesh guidance explains convex dynamic collision approximation.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`PropertiesDialog.__init__(scene_object, parent=None)`](../../src/properties_dialog.py#L9) | Build instance body-type, bounce, and velocity controls without mutating the source object. **Output:** None. Creates controls initialized from effective instance properties. |
| [`PropertiesDialog._markBounceChanged(value)`](../../src/properties_dialog.py#L76) | Record that bounce was edited so untouched file precision can otherwise be preserved. **Output:** None. Sets the bounce-changed flag. |
| [`PropertiesDialog.values()`](../../src/properties_dialog.py#L89) | Read edited bounce and velocity controls, preserving original precision for untouched fields. Body type is read separately from the checkbox. **Output:** tuple: Bounce float and three-component velocity list in m/s; does not apply them to the object. |

## Existing checks

[test_properties.py](../../Testing/Developer_Tests/test_properties.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[simuO](simuO.md), [scene](../Backend/scene.md), [physics_world](../Backend/physics_world.md).
