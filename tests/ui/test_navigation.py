"""Hierarchy view filters and keyboard interactions preserve editor state."""

import unittest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMainWindow

from tests.support.qt import get_application

from simuo.editor.state import EditorState
from simuo.ui.panels.hierarchy.panel import HierarchyPanel
from simuo.scene.model import Scene, SceneObject


class HierarchyNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()

    def setUp(self):
        self.scene = Scene()
        self.objects = [SceneObject(name) for name in ("Alpha", "Beta", "Alpine", "Delta")]
        self.objects[1].editor_visible = False
        self.objects[2].selection_locked = True
        self.objects[3].editor_visible = False
        self.objects[3].selection_locked = True
        for obj in self.objects:
            self.scene.addObject(obj)
        self.window = QMainWindow()
        self.state = EditorState(self.scene, self.window)
        self.panel = HierarchyPanel(self.state)
        self.window.setCentralWidget(self.panel)
        self.window.resize(340, 400)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        if self.app.platformName() != "offscreen":
            self.assertTrue(QTest.qWaitForWindowActive(self.window, 2000))
        self.app.processEvents()
        self.addCleanup(self.window.close)

    def keys(self, *indexes):
        return [self.objects[index].identifier for index in indexes]

    def filter(self, attribute, value):
        self.panel.filter_actions[attribute][value].trigger()

    def test_visibility_lock_and_search_filters_combine_without_editing_scene(self):
        self.state.select(self.objects[0].identifier)
        self.filter("visibility_filter", "hidden")
        self.assertEqual(self.panel.matching_ids(), self.keys(1, 3))
        self.filter("lock_filter", "locked")
        self.assertEqual(self.panel.matching_ids(), self.keys(3))
        self.assertIn("1 of 4 objects", self.panel.status.text())
        self.assertIn("1 selected (filtered)", self.panel.status.text())
        self.assertEqual(self.panel.filter_summary.text(), "Hidden · Locked")
        self.assertTrue(self.panel.filter_button.property("filterActive"))
        self.panel.search.setText("beta")
        self.assertEqual(self.panel.matching_ids(), [])
        self.assertEqual(self.panel.stack.currentIndex(), 1)
        self.filter("lock_filter", "unlocked")
        self.assertEqual(self.panel.matching_ids(), self.keys(1))
        self.panel.clear_filters_button.click()
        self.assertEqual(self.panel.search.text(), "beta")
        self.assertEqual(self.panel.matching_ids(), self.keys(1))
        self.assertFalse(self.panel.filter_button.property("filterActive"))
        self.assertIs(self.state.selected_object, self.objects[0])
        self.assertEqual(self.state.undo_stack.count(), 0)
        self.assertFalse(self.scene.dirty)

    def test_group_visibility_and_lock_are_included_in_filters(self):
        group = self.state.create_group("Assembly", self.keys(0, 1))
        self.state.set_group_visibility(group.identifier, False)
        self.state.set_group_locked(group.identifier, True)
        count = self.state.undo_stack.count()
        self.filter("visibility_filter", "hidden")
        self.filter("lock_filter", "locked")
        self.assertEqual(self.panel.matching_ids(), self.keys(0, 1, 3))
        self.panel.search.setText("assembly")
        self.assertEqual(self.panel.matching_ids(), self.keys(0, 1))
        self.state.undo_stack.undo()  # Unlock group, leaving its visibility hidden.
        self.assertEqual(self.panel.matching_ids(), [])
        self.assertTrue(self.objects[0].editor_visible)
        self.assertFalse(self.objects[0].selection_locked)
        self.assertEqual(self.state.undo_stack.count(), count)

    def test_filters_temporarily_expand_scene_and_groups_then_restore_collapse(self):
        group = self.state.create_group("Assembly", self.keys(0, 1))
        group.expanded = False
        self.panel._apply_filter()
        self.panel.scene_toggle.setChecked(False)
        self.filter("visibility_filter", "hidden")
        self.assertTrue(self.panel.scene_toggle.isChecked())
        self.assertFalse(self.panel.rows[self.objects[1].identifier].isHidden())
        self.assertFalse(group.expanded)
        self.filter("lock_filter", "unlocked")
        self.filter("visibility_filter", "all")
        self.assertTrue(self.panel.scene_toggle.isChecked())
        self.panel.filter_menu.actions()[-1].trigger()  # Reset Filters.
        self.assertFalse(self.panel.scene_toggle.isChecked())
        self.assertTrue(self.panel.rows[self.objects[1].identifier].isHidden())
        self.assertFalse(group.expanded)

    def test_show_selected_clears_all_filters_without_changing_visibility_or_selection(self):
        group = self.state.create_group("Assembly", self.keys(0, 1))
        self.state.select(self.objects[1].identifier)
        group.expanded = False
        self.filter("visibility_filter", "visible")
        self.filter("lock_filter", "locked")
        self.panel.search.setText("missing")
        count = self.state.undo_stack.count()
        self.panel.reveal_button.click()
        self.assertEqual(self.panel.search.text(), "")
        self.assertEqual(self.panel.visibility_filter, "all")
        self.assertEqual(self.panel.lock_filter, "all")
        self.assertTrue(group.expanded)
        self.assertFalse(self.panel.rows[self.objects[1].identifier].isHidden())
        self.assertFalse(self.objects[1].editor_visible)
        self.assertIs(self.state.selected_object, self.objects[1])
        self.assertEqual(self.state.undo_stack.count(), count)

    def test_filters_update_for_isolation_undo_and_redo(self):
        self.filter("visibility_filter", "hidden")
        self.state.select(self.objects[0].identifier)
        self.state.isolate_selected()
        self.assertEqual(self.panel.matching_ids(), self.keys(1, 2, 3))
        QTest.keyClick(self.panel, Qt.Key_Escape)
        self.assertIsNone(self.state.isolated_ids)
        self.assertEqual(self.panel.matching_ids(), self.keys(1, 3))
        self.state.set_visibility(self.objects[0].identifier, False)
        self.assertEqual(self.panel.matching_ids(), self.keys(0, 1, 3))
        self.state.undo_stack.undo()
        self.assertEqual(self.panel.matching_ids(), self.keys(1, 3))
        self.state.undo_stack.redo()
        self.assertEqual(self.panel.matching_ids(), self.keys(0, 1, 3))

    def test_keyboard_follows_only_matching_rows_and_modifier_navigation_preserves_selection(self):
        self.filter("visibility_filter", "visible")
        self.state.select(self.objects[0].identifier)
        first = self.panel.rows[self.objects[0].identifier]
        last = self.panel.rows[self.objects[2].identifier]
        QTest.keyClick(first.name_button, Qt.Key_Down, Qt.ControlModifier)
        self.assertEqual(self.state.selected_ids, tuple(self.keys(0)))
        self.assertEqual(self.panel._cursor_key, self.objects[2].identifier)
        QTest.keyClick(last.name_button, Qt.Key_Home)
        QTest.keyClick(first.visibility, Qt.Key_Down, Qt.ShiftModifier)
        self.assertEqual(set(self.state.selected_ids), set(self.keys(0, 2)))
        QTest.keyClick(last.lock, Qt.Key_Home)
        self.assertEqual(self.state.selected_ids, tuple(self.keys(0)))
        QTest.keyClick(first.name_button, Qt.Key_End)
        self.assertEqual(self.state.selected_ids, tuple(self.keys(2)))
        self.assertFalse(self.scene.dirty)

    def test_shift_navigation_starts_from_viewport_selection_and_keeps_anchor(self):
        self.state.select(self.objects[0].identifier)
        QTest.keyClick(self.panel.rows[self.objects[0].identifier].name_button, Qt.Key_Down, Qt.ShiftModifier)
        QTest.keyClick(self.panel.rows[self.objects[1].identifier].name_button, Qt.Key_Down, Qt.ShiftModifier)
        self.assertEqual(set(self.state.selected_ids), set(self.keys(0, 1, 2)))
        QTest.keyClick(self.panel.rows[self.objects[2].identifier].name_button, Qt.Key_Up, Qt.ShiftModifier)
        self.assertEqual(set(self.state.selected_ids), set(self.keys(0, 1)))

    def test_group_keyboard_selection_does_not_include_filtered_out_children(self):
        group = self.state.create_group("Assembly", self.keys(0, 1))
        self.filter("visibility_filter", "visible")
        QTest.keyClick(self.panel, Qt.Key_Home)
        self.assertEqual(self.panel._cursor_key, group.identifier)
        self.assertEqual(self.state.selected_ids, tuple(self.keys(0)))

    def test_escape_cancels_group_rename_and_text_arrows_do_not_navigate_rows(self):
        group = self.state.create_group("Assembly", self.keys(0, 1))
        row = self.panel.group_rows[group.identifier]
        self.state.select(self.objects[2].identifier)
        count = self.state.undo_stack.count()
        row.begin_rename()
        QTest.keyClicks(row.name_edit, "Discarded")
        QTest.keyClick(row.name_edit, Qt.Key_Left)
        self.assertIs(self.state.selected_object, self.objects[2])
        QTest.keyClick(row.name_edit, Qt.Key_Escape)
        self.assertEqual(group.name, "Assembly")
        self.assertEqual(row.name_stack.currentIndex(), 0)
        self.assertEqual(self.state.undo_stack.count(), count)
        self.panel.search.setText("Al")
        self.panel.search.setFocus()
        self.panel.search.setCursorPosition(2)
        QTest.keyClick(self.panel.search, Qt.Key_Left)
        self.assertEqual(self.panel.search.cursorPosition(), 1)
        self.assertIs(self.state.selected_object, self.objects[2])

    def test_clicking_no_results_or_panel_padding_clears_selection_and_navigation_anchor(self):
        self.state.select(self.objects[0].identifier)
        self.panel.search.setText("missing")
        QTest.mouseClick(self.panel.stack.widget(1), Qt.LeftButton)
        self.assertFalse(self.state.selected_ids)
        self.assertIsNone(self.panel._anchor_id)
        self.assertIsNone(self.panel._cursor_key)
        self.panel.search.clear()
        self.state.select(self.objects[2].identifier)
        QTest.mouseClick(self.panel, Qt.LeftButton)
        self.assertFalse(self.state.selected_ids)
        QTest.keyClick(self.panel, Qt.Key_Down)
        self.assertEqual(self.state.selected_ids, tuple(self.keys(0)))

    def test_drag_is_disabled_by_state_filters_and_new_group_clears_filters(self):
        self.panel.scene_toggle.setChecked(False)
        self.filter("lock_filter", "locked")
        self.assertIsNone(self.panel.decode_drag(self.panel.drag_mime("object", self.keys(2))))
        self.state.select(self.objects[0].identifier)
        self.panel.new_group.click()
        self.assertFalse(self.panel.has_active_filters())
        group = self.scene.groups[0]
        self.assertEqual(group.members, self.keys(0))
        self.assertFalse(self.panel.group_rows[group.identifier].isHidden())
        self.assertTrue(self.panel.scene_toggle.isChecked())
        self.assertTrue(self.panel.group_rows[group.identifier].isVisible())
