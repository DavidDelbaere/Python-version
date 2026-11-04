# temporary_parts.py: backend guide

Source: [src/temporary_parts.py](../../src/temporary_parts.py). [Documentation index](../README.md).

Manage unsaved OBJ import copies and provide atomic single-file replacement for documents, exports, and scenes.

## How it works

`TemporaryParts.create(source)` lazily allocates a temporary directory, copies the source bytes into a uniquely named `.simuOPart`, and records the original path. It preserves OBJ content rather than converting it to JSON. Import callers validate the copy.

`release(path)` deletes one registered copy; `cleanup()` removes all managed files and resets ownership. `atomic_write(path, contents)` writes bytes to a sibling staging file, flushes/fsyncs, then uses `os.replace()` and cleans up staging.

## Contracts and editing considerations

- `sources` maps temporary copy paths to their original source files. `directory` is `None` until allocated or after cleanup.
- `contains(None)` is False; other candidate paths are resolved before lookup.
- Temporary deletion must consider shared scene references: removing one instance must not release a copy used by another.
- `atomic_write()` validates neither schema nor destination policy. Its parent directory must exist; it provides no multi-file transaction.
- The source OBJ is never overwritten by creating/releasing a temporary copy.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`atomic_write(path, contents)`](../../src/temporary_parts.py#L8) | Write bytes to a sibling staging file, flush them, and atomically replace the destination. Clean up staging on failure; the parent directory must exist. **Output:** None. Replaces one file; filesystem errors propagate. |
| [`TemporaryParts.__init__()`](../../src/temporary_parts.py#L36) | Initialize an empty temporary-part registry without allocating a directory yet. **Output:** None. |
| [`TemporaryParts.directory()`](../../src/temporary_parts.py#L46) | Expose the allocated temporary directory, if any. **Output:** pathlib.Path or None: Directory path, or None before allocation or after cleanup. |
| [`TemporaryParts.create(source)`](../../src/temporary_parts.py#L55) | Copy source bytes into a uniquely named temporary .simuOPart and register its origin. Does not validate or convert the copied geometry. **Output:** pathlib.Path: Temporary copy; filesystem errors propagate. |
| [`TemporaryParts.contains(path)`](../../src/temporary_parts.py#L81) | Check whether a resolved path is registered as a temporary part. **Output:** bool: True for a managed copy; False for None or an unregistered path. |
| [`TemporaryParts.release(path)`](../../src/temporary_parts.py#L92) | Delete and unregister a managed copy, leaving its source untouched. **Output:** None. Unregistered paths are ignored; filesystem errors propagate. |
| [`TemporaryParts.cleanup()`](../../src/temporary_parts.py#L106) | Remove the temporary directory and clear all registered copies. **Output:** None. Resets directory ownership and the source mapping. |

## Existing checks

[test_obj_import.py](../../Testing/Developer_Tests/test_obj_import.py), [test_portability.py](../../Testing/Developer_Tests/test_portability.py), [test_scene_deletion.py](../../Testing/Developer_Tests/test_scene_deletion.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[simuO](simuO.md), [part_document](part_document.md), [feature_document](feature_document.md), [part_export](part_export.md).
