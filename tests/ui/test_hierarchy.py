"""Outliner behavior with native row widgets, filtering and mouse controls."""

import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMainWindow

from tests.support.qt import get_application

from simuo.editor.state import EditorState
from simuo.ui.panels.hierarchy.panel import HierarchyPanel
from simuo.scene.model import Scene, SceneObject


class HierarchyWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()

    def setUp(self):
        self.window = QMainWindow()
        self.addCleanup(self.window.close)
        self.scene = Scene()
        self.objects = [SceneObject(name) for name in ("Alpha", "Beta", "Alpine")]
        for obj in self.objects:
            self.scene.addObject(obj)
        self.state = EditorState(self.scene, self.window)
        self.panel = HierarchyPanel(self.state)
        self.window.setCentralWidget(self.panel)
        self.window.resize(340, 350)
        self.window.show()
        self.app.processEvents()

    def test_search_preserves_selection_and_restores_its_row_highlight(self):
        selected = self.objects[1]
        self.state.select(selected.identifier)
        self.panel.search.setText("AL")
        self.assertIs(self.state.selected_object, selected)
        self.assertIn("2 of 3 objects", self.panel.status.text())
        self.assertIn("1 selected (filtered)", self.panel.status.text())
        self.assertNotIn(selected.identifier, self.panel.matching_ids())
        self.panel.search.clear()
        rows = [identifier for identifier, row in self.panel.rows.items() if row.is_selected]
        self.assertEqual(rows, [selected.identifier])
        self.assertEqual(self.panel.status.text(), "3 objects · 1 selected")
        self.assertFalse(self.scene.dirty)

    def test_inline_rename_can_filter_itself_out_without_losing_selection(self):
        obj = self.objects[0]
        self.state.select(obj.identifier)
        self.panel.search.setText("alpha")
        row = self.panel.rows[obj.identifier]
        row.begin_rename()
        row.name_edit.setText("Gamma")
        row.finish_rename()
        self.assertEqual(obj.name, "Gamma")
        self.assertIs(self.state.selected_object, obj)
        self.assertEqual(self.panel.stack.currentIndex(), 1)
        self.assertIn("0 of 3", self.panel.status.text())
        self.panel.search.clear()
        self.assertEqual(self.panel.rows[obj.identifier].name_button.full_name, "Gamma")
        self.assertEqual(self.panel.selected_id, obj.identifier)

    def test_visibility_and_lock_clicks_do_not_select_a_different_row(self):
        target, selected, _ = self.objects
        self.state.select(selected.identifier)
        for column in (1, 2):
            QTest.mouseClick(self.panel.rows[target.identifier].visibility if column == 1 else self.panel.rows[target.identifier].lock, Qt.LeftButton)
            self.assertIs(self.state.selected_object, selected)
            self.assertEqual(self.panel.selected_id, selected.identifier)
        self.assertFalse(target.editor_visible)
        self.assertTrue(target.selection_locked)
        self.assertTrue(selected.editor_visible)
        self.assertFalse(selected.selection_locked)
        self.assertTrue(self.scene.dirty)

    def test_hiding_and_locking_the_selected_object_keeps_it_inspectable(self):
        obj = self.objects[0]
        self.state.select(obj.identifier)
        QTest.mouseClick(self.panel.rows[obj.identifier].visibility, Qt.LeftButton)
        QTest.mouseClick(self.panel.rows[obj.identifier].lock, Qt.LeftButton)
        self.assertIs(self.state.selected_object, obj)
        self.assertEqual(self.panel.selected_id, obj.identifier)
        self.assertFalse(obj.editor_visible)
        self.assertTrue(obj.selection_locked)
        self.assertEqual(self.panel.rows[obj.identifier].visibility.toolTip(), "Show in viewport")
        self.assertEqual(self.panel.rows[obj.identifier].lock.toolTip(), "Unlock viewport selection")

    def test_releasing_a_control_on_another_row_does_not_toggle_either_object(self):
        button = self.panel.rows[self.objects[0].identifier].visibility
        QTest.mousePress(button, Qt.LeftButton)
        QTest.mouseRelease(button, Qt.LeftButton, pos=button.rect().bottomRight() * 3)
        self.assertTrue(all(obj.editor_visible for obj in self.objects))
        self.assertFalse(self.scene.dirty)

    def test_frame_key_is_scoped_to_tree_and_does_not_intercept_search_typing(self):
        obj = self.objects[0]
        self.state.select(obj.identifier)
        frames = []
        self.state.frame_requested.connect(frames.append)
        QTest.keyClick(self.panel, Qt.Key_F)
        self.assertEqual(frames, [obj])
        QTest.keyClicks(self.panel.search, "f")
        self.assertEqual(self.panel.search.text(), "f")
        self.assertEqual(frames, [obj])
        self.state.set_visibility(obj.identifier, False)
        QTest.keyClick(self.panel, Qt.Key_F)
        self.assertEqual(frames, [obj])

    def test_context_menu_actions_control_visibility_locking_and_framing(self):
        obj = self.objects[0]
        self.state.select(obj.identifier)
        frames = []
        self.state.frame_requested.connect(frames.append)
        menu = self.panel.context_menu(obj.identifier)
        self.addCleanup(menu.deleteLater)
        next(action for action in menu.actions() if action.text().startswith("Frame Selected")).trigger()
        self.assertEqual(frames, [obj])
        next(action for action in menu.actions() if action.text() == "Hide in Viewport").trigger()
        next(action for action in menu.actions() if action.text() == "Lock Viewport Selection").trigger()
        self.assertFalse(obj.editor_visible)
        self.assertTrue(obj.selection_locked)
        updated = self.panel.context_menu(obj.identifier)
        self.addCleanup(updated.deleteLater)
        self.assertFalse(next(action for action in updated.actions() if action.text().startswith("Frame Selected")).isEnabled())

    def test_scene_header_counts_and_collapse_survive_edits_and_search(self):
        self.state.set_scene_name("Experiment")
        self.assertIn("Experiment", self.panel.scene_toggle.text())
        self.state.select(self.objects[1].identifier)
        self.panel.scene_toggle.setChecked(False)
        self.state.set_selection_locked(self.objects[0].identifier, True)
        self.assertFalse(self.panel.scene_toggle.isChecked())
        self.panel.search.setText("Al")
        self.panel.search.clear()
        self.assertFalse(self.panel.scene_toggle.isChecked())
        self.state.add_object(SceneObject("Delta"))
        self.assertIn("4 objects", self.panel.status.text())

    def test_empty_scene_and_no_search_results_have_distinct_messages(self):
        self.panel.search.setText("does not exist")
        self.assertEqual(self.panel.stack.currentIndex(), 1)
        self.state.replace_objects([])
        self.assertEqual(self.panel.stack.currentIndex(), 0)
        self.assertIn("0 objects", self.panel.status.text())

    def test_row_controls_follow_reloaded_objects_with_the_same_ids(self):
        previous = self.objects[0]
        replacement = SceneObject("Reloaded", identifier=previous.identifier)
        replacement.editor_visible = False
        self.state.replace_objects([replacement])
        row = self.panel.rows[replacement.identifier]
        self.assertIs(row.obj, replacement)
        row.visibility.click()
        self.assertTrue(replacement.editor_visible)
        self.assertTrue(previous.editor_visible)
        self.assertEqual(row.name_button.full_name, "Reloaded")

    def test_context_menu_opens_from_the_object_name_button(self):
        obj = self.objects[0]
        button = self.panel.rows[obj.identifier].name_button
        menu = Mock()
        with patch.object(self.panel, "context_menu", return_value=menu):
            QTest.mouseClick(button, Qt.RightButton)
            menu.exec.assert_called_once()
        self.assertIs(self.state.selected_object, obj)

    def test_frame_key_bubbles_from_object_name_controls(self):
        obj = self.objects[0]
        self.state.select(obj.identifier)
        frames = []
        self.state.frame_requested.connect(frames.append)
        QTest.keyClick(self.panel.rows[obj.identifier].name_button, Qt.Key_F)
        self.assertEqual(frames, [obj])

    def test_modifier_clicks_toggle_and_select_filtered_ranges(self):
        a, b, c = self.objects
        button = lambda obj: self.panel.rows[obj.identifier].name_button
        QTest.mouseClick(button(a), Qt.LeftButton)
        QTest.mouseClick(button(c), Qt.LeftButton, Qt.ControlModifier)
        self.assertEqual(self.state.selected_objects, (a, c))
        self.assertTrue(self.panel.rows[a.identifier].is_selected)
        self.assertTrue(self.panel.rows[c.identifier].is_selected)
        self.assertIn("2 selected", self.panel.status.text())
        QTest.mouseClick(button(a), Qt.LeftButton, Qt.ControlModifier)
        self.assertEqual(self.state.selected_objects, (c,))
        QTest.mouseClick(button(a), Qt.LeftButton)
        self.panel.search.setText("al")
        QTest.mouseClick(button(c), Qt.LeftButton, Qt.ShiftModifier)
        self.assertEqual(set(self.state.selected_objects), {a, c})
        self.assertIs(self.state.selected_object, c)
        self.assertFalse(self.scene.dirty)

    def test_shift_range_keeps_anchor_when_extending_and_shrinking(self):
        a, b, c = self.objects
        QTest.mouseClick(self.panel.rows[a.identifier].name_button, Qt.LeftButton)
        QTest.mouseClick(self.panel.rows[c.identifier].name_button, Qt.LeftButton, Qt.ShiftModifier)
        self.assertEqual(set(self.state.selected_objects), {a, b, c})
        QTest.mouseClick(self.panel.rows[b.identifier].name_button, Qt.LeftButton, Qt.ShiftModifier)
        self.assertEqual(self.state.selected_objects, (a, b))

    def test_context_actions_preserve_and_operate_on_the_selection(self):
        a, b, _ = self.objects
        self.state.select_many([a.identifier, b.identifier])
        menu = self.panel.context_menu(a.identifier)
        self.addCleanup(menu.deleteLater)
        with patch.object(self.panel, "context_menu", return_value=Mock()):
            QTest.mouseClick(self.panel.rows[a.identifier].name_button, Qt.RightButton)
        self.assertEqual(self.state.selected_objects, (a, b))
        next(action for action in menu.actions() if action.text() == "Hide in Viewport").trigger()
        self.assertFalse(a.editor_visible)
        self.assertFalse(b.editor_visible)
        self.state.undo_stack.undo()
        self.assertTrue(a.editor_visible and b.editor_visible)
        next(action for action in menu.actions() if action.text() == "Duplicate").trigger()
        self.assertEqual(len(self.scene.objects), 5)
        self.state.undo_stack.undo()
        self.assertEqual(self.state.selected_objects, (a, b))
        next(action for action in menu.actions() if action.text() == "Delete").trigger()
        self.assertEqual(self.scene.objects, [self.objects[2]])

    def test_escape_cancels_inline_rename_without_an_undo_entry(self):
        row = self.panel.rows[self.objects[0].identifier]
        row.begin_rename()
        QTest.keyClicks(row.name_edit, "Discard this")
        QTest.keyClick(row.name_edit, Qt.Key_Escape)
        self.assertEqual(self.objects[0].name, "Alpha")
        self.assertEqual(row.name_stack.currentIndex(), 0)
        self.assertFalse(self.state.undo_stack.canUndo())

    def test_blank_space_clears_selection_but_row_background_selects(self):
        a = self.objects[0]
        QTest.mouseClick(self.panel.rows[a.identifier], Qt.LeftButton)
        self.assertEqual(self.state.selected_objects, (a,))
        QTest.mouseClick(self.panel.scroll.widget(), Qt.LeftButton,
                         pos=self.panel.scroll.widget().rect().bottomLeft())
        self.assertFalse(self.state.selected_objects)
