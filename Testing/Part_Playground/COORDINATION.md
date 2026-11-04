# Handoff for the Linux implementation and testing agents

> Historical handoff from the original implementation. Production source is in `src`, current tests are in `Testing/Developer_Tests`, and current guides are indexed in [developer documentation](../../Documentation/README.md). Report filenames and earlier implementation status below are archival references.

## Live Render update, 2026-11-02

The user requested a Render option and a separate live physics window. Added
`src/physics_world.py`, `src/physics_render.py`, menu/toolbar integration in
`src/simuO.py`, preservation of mass_source in `src/part_format.py`, and PyBullet
3.2.7 in `src/requirements.txt`. PHYSICS_RENDER.md records behavior and validation.
The project's .venv has the dependency installed. All 41 automated tests,
including the other agents' OBJ import/save and project safety checks, pass.
The real desktop Render/playback integration test also passes. The Linux/OBJ
workflow source changes were preserved. No packaged binary was rebuilt.

## Production migration update, 2026-11-02

The user subsequently authorized migrating the main renderer. Production changes
now touch `src/renderer.py`, `src/simuO.py`, `src/scene.py`, and add
`src/part_format.py`, `src/part_assets.py`, `Assets/aluminum_cube.simuOPart`,
`tests/` and `PART_MIGRATION.md`. The experiment remains independent. The scope
and incompatibility notes below describe the original experiment before this
authorization. Linux launcher/startup/build changes are preserved.

JSON and OBJ parts now both render in the main editor. The other tester's
extreme-number findings in PART_TEST_RESULTS.md informed clean numeric failures
in the production path. See PART_MIGRATION.md for validation and integration
limits. This is a filesystem handoff; no direct agent session was available.

This experiment is owned by the part-format task. All changes stay in
`Testing/Part_Playground/`; no production files, requirements, assets, or launchers
are modified. Please leave this folder independent of Linux compatibility edits.

The existing README and TEST_RESULTS.md were consulted. Other running agent
sessions are not exposed to this task's collaboration tools, so this file is the
shared filesystem handoff. Add integration questions here if needed.

The new `.simuOPart` files are JSON, whereas existing assets are OBJ text. Do not
send the new sample through the current OBJ loader. Future integration should
detect JSON by content, dispatch by `format` and `version`, and retain the old
OBJ path. No production migration is part of this experiment.

Run `python3 Testing/Part_Playground/viewer.py` for the independent viewer.
Run `python3 -m unittest discover -s Testing/Part_Playground -v` for checks.

Completion handoff: FORMAT.md describes the ideal design and exact v1 contract;
the sample, independent Tk/software renderer, and 11 passing checks are ready.
Real desktop smoke testing passed with 40 rendered frames and physics advancing.
See VALIDATION.md for evidence and limits. IMPLEMENTATION_NOTES.md was also
reviewed; this experiment does not touch the startup callback or launcher work.

## Independent tester handoff, 2026-11-02

See root `PART_TEST_RESULTS.md` for executed checks and reproductions. The sample,
normal-range physics, author suite (11/11), and desktop rendering/controls pass.
Found extreme-range robustness issues: accepted position `[1e16,1.1,0]` or
explicit-mass dimensions `[1e-100,1e-100,1e-100]` cause `ZeroDivisionError` in the
renderer; huge integer density or squared dimensions raise raw `OverflowError`
in validation. No implementation fixes were made by the tester. Independent
harnesses are `/tmp/simuo_part_qa.py` and `/tmp/simuo_part_gui_qa.py`.

## Usability feedback from independent tester (2026-11-02)

The user explicitly asks both implementing agents to prioritize user friendliness and regression tests. The prototype's labeled playback controls, on-screen orbit/zoom instructions, and invalid-file dialog are useful. Please keep the main editor integration equally clear: importing JSON parts must visibly frame the part, retain legacy OBJ support, explain invalid input in a dialog, and preserve the current scene on failure. Update the main README, which currently says all `.simuOPart` files contain OBJ geometry, and distinguish editor functionality from the standalone lab's physics playback. Keep the numerical robustness findings above visible until resolved. Independent test results will be added to root TEST_RESULTS.md.

Executed follow-up: 11 lab tests and all six independent desktop interaction checks pass; the production integration's 9 tests and real GPU integration check also pass, including framing, mixed imports, relative save/reload, and preserving scene on invalid input. Production editor still has confirmed unsaved Open/Close and failed Save As usability defects; see root TEST_RESULTS.md. Please coordinate ownership through the shared handoffs and update README's OBJ-only statement before completion.
