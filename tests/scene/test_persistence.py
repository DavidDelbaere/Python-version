"""Project-file compatibility and separation from transient editor state."""

import json
from pathlib import Path
import tempfile
import unittest

from tests.support.paths import ROOT
from simuo.scene.model import Scene, SceneObject, SceneGroup
from simuo.scene.persistence import load_project, save_project


class ProjectPersistence(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "scene.simuO"

    def test_round_trip_preserves_identity_order_groups_and_precise_transforms(self):
        scene = Scene()
        a, b = SceneObject("Cube"), SceneObject("Cube")
        a.meshPath = ROOT / "Assets/cube.simuOPart"
        b.meshPath = Path("Assets/cube.simuOPart")
        a.position = [1.123456789, -2.0, 3.0]
        b.scale = [-1.0, 2.5, 0.0]
        b.editor_visible = False
        b.selection_locked = True
        for obj in (a, b):
            scene.addObject(obj)
        group = SceneGroup("Assemblée")
        group.members = [b.identifier, a.identifier]
        group.editor_visible = False
        group.selection_locked = True
        group.expanded = False
        scene.groups = [group]
        scene.root_order = [group.identifier]
        save_project(scene, self.path)
        objects, groups, roots = load_project(self.path)
        self.assertEqual([obj.identifier for obj in objects], [a.identifier, b.identifier])
        self.assertEqual(objects[0].position, a.position)
        self.assertEqual(objects[1].scale, b.scale)
        self.assertEqual(objects[0].meshPath, a.meshPath)
        self.assertEqual(objects[1].meshPath, b.meshPath)
        self.assertEqual(groups[0].members, group.members)
        self.assertEqual(groups[0].name, group.name)
        self.assertFalse(groups[0].expanded)
        self.assertTrue(groups[0].selection_locked)
        self.assertFalse(groups[0].editor_visible)
        self.assertEqual(roots, scene.root_order)

    def test_legacy_defaults_and_invalid_optional_group_data_remain_compatible(self):
        self.path.write_text(json.dumps({"objects": [
            {"name": "Old"}, {"name": "Invalid flags", "editor": {"visible": "no", "selection_locked": 1}},
        ], "groups": [None, {"name": "Empty", "objects": "invalid", "expanded": "no"}],
            "hierarchy_order": "invalid"}))
        objects, groups, roots = load_project(self.path)
        self.assertEqual(len({obj.identifier for obj in objects}), 2)
        self.assertTrue(all(obj.editor_visible and not obj.selection_locked for obj in objects))
        self.assertEqual(objects[0].scale, [1, 1, 1])
        self.assertEqual(groups[0].members, [])
        self.assertTrue(groups[0].expanded)
        self.assertEqual(roots, [])

    def test_save_excludes_isolation_and_does_not_mark_scene_clean(self):
        scene = Scene()
        obj = SceneObject("Hidden in local view")
        obj._isolated_out = True
        scene.addObject(obj)
        scene.dirty = True
        save_project(scene, self.path)
        self.assertTrue(scene.dirty)
        self.assertTrue(obj._isolated_out)
        objects, _, _ = load_project(self.path)
        self.assertTrue(objects[0].viewport_visible)
