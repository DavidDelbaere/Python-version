# resources.py: backend guide

Source: [src/resources.py](../../src/resources.py). [Documentation index](../README.md).

Locate shipped images and assets consistently in source checkouts and PyInstaller bundles.

## How it works

`resource_path(*parts)` selects the repository root in a normal interpreter or `sys._MEIPASS` in a frozen application, then joins the supplied components. It returns a `Path` and does not check whether the resource exists.

## Contracts and editing considerations

- Paths are relative to the application root, not the current working directory.
- Packaging must collect each resource directory used by callers.
- Moving this module deeper changes the meaning of `Path(__file__).resolve().parent.parent`; update that root calculation if relocating it.

## Function reference

Signatures list inputs; behavior and output summarize the source docstrings. Full parameter types, units, and edge cases are documented beside each function in the source. Properties appear as zero-argument getters; setters are marked separately.

| Function / parameters | Behavior and output |
| --- | --- |
| [`resource_path(*parts)`](../../src/resources.py#L7) | Locate an application resource relative to the checkout or PyInstaller extraction directory, independently of the current working directory. **Output:** pathlib.Path: Joined resource path; existence is not checked. |

## Existing checks

[test_portability.py](../../Testing/Developer_Tests/test_portability.py). Test locations and the current reorganization caveat are explained in the documentation index. GUI scripts require a working desktop/graphics environment.

## Related documentation

[main](../Frontend/main.md), [startMenu](../Frontend/startMenu.md), [project_paths](project_paths.md), [main.spec](../../src/main.spec).
