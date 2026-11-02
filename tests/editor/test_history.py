"""Reversible scene edits, saved checkpoints, and multi-object operations."""

import unittest

from tests.support.qt import get_application

from simuo.editor.state import EditorState
from simuo.scene.model import Scene, SceneObject


class EditHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()

    def setUp(self):
        self.scene = Scene()
        self.objects = [SceneObject(name) for name in ("Cube", "Cube.001", "Other")]
        for obj in self.objects:
            self.scene.addObject(obj)
        self.state = EditorState(self.scene)
        self.stack = self.state.undo_stack

    def test_all_property_edits_round_trip_without_changing_selection(self):
        obj = self.objects[0]
        obj.position = [1.123456789, 2, 3]
        self.state.select(obj.identifier)
        self.state.rename_object(obj.identifier, "Renamed")
        self.state.set_visibility(obj.identifier, False)
        self.state.set_selection_locked(obj.identifier, True)
        self.state.set_transform_component(obj.identifier, "position", 0, 20)
        self.state.reset_transform(obj.identifier)
        self.assertEqual(self.stack.count(), 5)
        for _ in range(5):
            self.stack.undo()
        self.assertEqual(obj.name, "Cube")
        self.assertEqual(obj.position, [1.123456789, 2, 3])
        self.assertTrue(obj.editor_visible)
        self.assertFalse(obj.selection_locked)
        self.assertIs(self.state.selected_object, obj)
        self.assertFalse(self.scene.dirty)
        for _ in range(5):
            self.stack.redo()
        self.assertEqual(obj.name, "Renamed")
        self.assertEqual(obj.position, [0, 0, 0])
        self.assertFalse(obj.editor_visible)
        self.assertTrue(obj.selection_locked)

    def test_save_checkpoint_tracks_undo_redo_and_history_branches(self):
        obj = self.objects[0]
        self.state.rename_object(obj.identifier, "Saved")
        self.state.mark_saved()
        self.assertFalse(self.scene.dirty)
        self.state.set_visibility(obj.identifier, False)
        self.assertTrue(self.scene.dirty)
        self.stack.undo()
        self.assertFalse(self.scene.dirty)
        self.stack.undo()
        self.assertTrue(self.scene.dirty)
        self.stack.redo()
        self.assertFalse(self.scene.dirty)
        self.stack.undo()
        self.state.rename_object(obj.identifier, "New branch")
        self.assertTrue(self.scene.dirty)
        self.assertFalse(self.stack.canRedo())
        self.stack.undo()
        self.assertTrue(self.scene.dirty)  # The saved state was discarded.

    def test_noops_and_selection_do_not_pollute_history_or_clear_redo(self):
        obj = self.objects[0]
        self.state.rename_object(obj.identifier, "Changed")
        self.stack.undo()
        self.state.select_many([obj.identifier, obj.identifier, "missing"])
        self.state.rename_object(obj.identifier, " ")
        self.state.rename_object(obj.identifier, "Cube")
        self.state.set_transform_component(obj.identifier, "position", 0, float("nan"))
        self.state.set_visibility(obj.identifier, True)
        self.state.reset_transform(obj.identifier)
        self.assertTrue(self.stack.canRedo())
        self.assertEqual(self.stack.count(), 1)
        self.assertFalse(self.scene.dirty)
        self.assertEqual(self.state.selected_ids, (obj.identifier,))

    def test_batch_transform_and_reset_each_undo_as_one_action(self):
        a, b, other = self.objects
        a.position = [1.123456, 2, 3]
        b.position = [7, 8, 9]
        self.state.select_many([a.identifier, b.identifier])
        self.state.set_transform_components(self.state.selected_ids, "position", 0, 40)
        self.assertEqual((a.position[0], b.position[0], other.position[0]), (40, 40, 0))
        self.assertEqual(self.stack.count(), 1)
        self.stack.undo()
        self.assertEqual(a.position, [1.123456, 2, 3])
        self.assertEqual(b.position, [7, 8, 9])
        self.stack.redo()
        self.state.reset_transforms(self.state.selected_ids)
        self.assertEqual(a.position, [0, 0, 0])
        self.assertEqual(b.position, [0, 0, 0])
        self.stack.undo()
        self.assertEqual(a.position, [40, 2, 3])
        self.assertEqual(b.position, [40, 8, 9])

    def test_batch_visibility_and_locking_restore_individual_values(self):
        a, b, _ = self.objects
        a.editor_visible = False
        b.selection_locked = True
        keys = [a.identifier, b.identifier]
        self.state.set_objects_visibility(keys, False)
        self.state.set_objects_locked(keys, True)
        self.stack.undo()
        self.assertFalse(a.selection_locked)
        self.assertTrue(b.selection_locked)
        self.stack.undo()
        self.assertFalse(a.editor_visible)
        self.assertTrue(b.editor_visible)

    def test_duplicate_has_unique_names_independent_vectors_and_stable_redo_ids(self):
        a, b, _ = self.objects
        a.position = [1, 2, 3]
        a.velocity = [4, 5, 6]
        a.editor_visible = False
        a.selection_locked = True
        self.state.select_many([a.identifier, b.identifier])
        self.state.duplicate_selected()
        copies = self.state.selected_objects
        self.assertEqual([obj.name for obj in copies], ["Cube.002", "Cube.003"])
        self.assertEqual(len({obj.identifier for obj in self.scene.objects}), 5)
        self.assertEqual(copies[0].position, a.position)
        self.assertIsNot(copies[0].position, a.position)
        self.assertIsNot(copies[0].velocity, a.velocity)
        self.assertFalse(copies[0].editor_visible)
        self.assertTrue(copies[0].selection_locked)
        ids = self.state.selected_ids
        self.stack.undo()
        self.assertEqual(self.scene.objects, self.objects)
        self.assertEqual(self.state.selected_objects, (a, b))
        self.stack.redo()
        self.assertEqual(self.state.selected_ids, ids)
        self.assertEqual(self.state.selected_objects, copies)
        self.state.set_transform_components(ids, "position", 1, 100)
        self.assertEqual(a.position[1], 2)

    def test_delete_restores_scene_order_selection_and_edited_values(self):
        a, b, c = self.objects
        self.state.rename_object(a.identifier, "Edited")
        self.state.select_many([c.identifier, a.identifier])
        self.state.delete_selected()
        self.assertEqual(self.scene.objects, [b])
        self.assertFalse(self.state.selected_objects)
        self.stack.undo()
        self.assertEqual(self.scene.objects, [a, b, c])
        self.assertEqual(self.state.selected_objects, (c, a))
        self.assertEqual(a.name, "Edited")
        self.stack.undo()
        self.assertEqual(a.name, "Cube")
        self.stack.redo()
        self.stack.redo()
        self.assertEqual(self.scene.objects, [b])

    def test_import_undo_and_scene_replacement_reset_history(self):
        a = self.objects[0]
        self.state.select(a.identifier)
        imported = SceneObject("Import")
        self.state.add_object(imported)
        self.state.select(imported.identifier)
        self.stack.undo()
        self.assertEqual(self.scene.objects, self.objects)
        self.assertIs(self.state.selected_object, a)
        self.stack.redo()
        self.assertIn(imported, self.scene.objects)
        self.state.replace_objects([SceneObject("New scene")])
        self.assertEqual(self.stack.count(), 0)
        self.assertFalse(self.state.selected_objects)
        self.assertFalse(self.scene.dirty)
        self.stack.undo()
        self.assertEqual(len(self.scene.objects), 1)

    def test_multiple_frame_request_includes_only_visible_selected_objects(self):
        self.state.select_many(obj.identifier for obj in self.objects)
        self.objects[1].editor_visible = False
        frames = []
        self.state.frame_requested.connect(frames.append)
        self.state.frame_selected()
        self.assertEqual(frames, [(self.objects[0], self.objects[2])])
