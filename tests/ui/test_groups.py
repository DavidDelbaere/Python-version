"""Group organization, inherited controls, navigation and native drag/drop events."""

import json
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEvent, QMimeData, QPoint, QPointF, Qt
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMainWindow

from tests.support.qt import get_application

from simuo.editor.state import EditorState
from simuo.ui.panels.hierarchy.panel import HierarchyPanel
from simuo.scene.model import Scene, SceneGroup, SceneObject


class GroupWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()

    def setUp(self):
        self.scene = Scene()
        self.objects = [SceneObject(name) for name in ("Alpha", "Beta", "Gamma", "Delta")]
        for obj in self.objects:
            self.scene.addObject(obj)
        self.state = EditorState(self.scene)
        self.window = QMainWindow()
        self.panel = HierarchyPanel(self.state)
        self.window.setCentralWidget(self.panel)
        self.window.resize(360, 420)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        if self.app.platformName() != "offscreen":
            self.assertTrue(QTest.qWaitForWindowActive(self.window, 2000))
        self.app.processEvents()
        self.addCleanup(self.window.close)

    def keys(self, objects):
        return [obj.identifier for obj in objects]

    def make_group(self, name="Assembly", objects=None):
        return self.state.create_group(name, self.keys(self.objects[:2] if objects is None else objects))

    def test_grouping_and_removal_round_trip_without_changing_objects(self):
        a, b, c, d = self.objects
        a.position = [12.5, 3, 4]
        a.rotation = [0, 30, 90]
        original = self.state.organization()
        self.state.select_many([a.identifier, b.identifier])
        group = self.make_group()
        self.assertEqual(group.members, [a.identifier, b.identifier])
        self.assertEqual(self.scene.root_order, [group.identifier, c.identifier, d.identifier])
        self.assertEqual(a.position, [12.5, 3, 4])
        self.assertEqual(a.rotation, [0, 30, 90])
        self.assertEqual(self.state.selected_objects, (a, b))
        self.assertEqual(self.state.undo_stack.count(), 1)
        self.state.undo_stack.undo()
        self.assertEqual(self.state.organization(), original)
        self.state.undo_stack.redo()
        self.state.remove_group(group.identifier)
        self.assertEqual(self.scene.objects, self.objects)
        self.assertEqual(self.scene.root_order, self.keys(self.objects))
        self.state.undo_stack.undo()
        self.assertIs(self.scene.groups[0], group)
        self.assertEqual(group.members, [a.identifier, b.identifier])

    def test_group_rename_remains_undoable_after_structure_restoration(self):
        group = self.make_group()
        self.state.rename_group(group.identifier, "Renamed")
        self.state.move_objects([self.objects[2].identifier], group.identifier)
        self.state.remove_group(group.identifier)
        for _ in range(3):
            self.state.undo_stack.undo()
        self.assertIs(self.scene.groups[0], group)
        self.assertEqual(group.name, "Assembly")
        self.state.undo_stack.redo()
        self.assertEqual(group.name, "Renamed")

    def test_move_block_keeps_visual_order_and_undo_restores_each_parent(self):
        a, b, c, d = self.objects
        first = self.make_group(objects=[a, c])
        second = self.make_group("Second", objects=[b])
        before = self.state.organization()
        self.state.select_many([d.identifier, c.identifier])
        self.state.move_objects(self.state.selected_ids, second.identifier, b.identifier)
        self.assertEqual(second.members, [c.identifier, d.identifier, b.identifier])
        self.assertEqual(first.members, [a.identifier])
        self.assertEqual(self.state.selected_objects, (d, c))
        self.state.undo_stack.undo()
        self.assertEqual(self.state.organization(), before)
        self.assertFalse(self.state.move_objects([a.identifier], "missing"))
        self.assertFalse(self.state.move_objects([a.identifier], first.identifier, a.identifier))

    def test_duplicate_and_delete_preserve_group_membership_and_order(self):
        group = self.make_group()
        a, b = self.objects[:2]
        self.state.select(a.identifier)
        self.state.duplicate_selected()
        copy = self.state.selected_object
        self.assertEqual(group.members, [a.identifier, copy.identifier, b.identifier])
        self.state.delete_selected()
        self.assertEqual(group.members, [a.identifier, b.identifier])
        self.state.undo_stack.undo()
        self.assertEqual(group.members, [a.identifier, copy.identifier, b.identifier])
        self.state.undo_stack.undo()
        self.assertEqual(group.members, [a.identifier, b.identifier])
        self.assertIs(self.state.selected_object, a)

    def test_group_visibility_and_lock_inherit_without_overwriting_individual_flags(self):
        group = self.make_group()
        a, b, c, _ = self.objects
        b.editor_visible = False
        b.selection_locked = True
        row = self.panel.group_rows[group.identifier]
        row.visibility.click()
        row.lock.click()
        self.assertTrue(a.editor_visible)
        self.assertFalse(a.viewport_visible)
        self.assertFalse(a.selection_locked)
        self.assertTrue(a.viewport_locked)
        self.assertFalse(b.viewport_visible)
        self.state.move_objects([c.identifier], group.identifier)
        self.assertFalse(c.viewport_visible)
        self.assertTrue(c.viewport_locked)
        self.state.undo_stack.undo()
        self.assertTrue(c.viewport_visible)
        self.assertFalse(c.viewport_locked)
        row.lock.click()
        row.visibility.click()
        self.assertTrue(a.viewport_visible)
        self.assertFalse(a.viewport_locked)
        self.assertFalse(b.viewport_visible)
        self.assertTrue(b.viewport_locked)

    def test_empty_groups_are_visible_and_new_group_starts_inline_rename(self):
        self.panel.new_group.click()
        group = self.scene.groups[0]
        row = self.panel.group_rows[group.identifier]
        self.assertEqual(group.members, [])
        self.assertEqual(self.panel.stack.currentIndex(), 2)
        self.assertEqual(row.name_stack.currentIndex(), 1)
        row.name_edit.setText("Empty Folder")
        row.finish_rename()
        self.assertEqual(group.name, "Empty Folder")
        self.assertIn("1 group", self.panel.status.text())

    def test_collapse_search_and_show_selected_preserve_view_state(self):
        group = self.make_group()
        a = self.objects[0]
        self.panel.toggle_group(group.identifier)
        self.assertFalse(group.expanded)
        self.assertTrue(self.panel.rows[a.identifier].isHidden())
        self.panel.search.setText("Assembly")
        self.assertEqual(self.panel.matching_ids(), group.members)
        self.assertFalse(self.panel.rows[a.identifier].isHidden())
        self.assertFalse(group.expanded)
        self.panel.search.clear()
        self.assertTrue(self.panel.rows[a.identifier].isHidden())
        self.state.select(a.identifier)
        self.panel.toggle_group(group.identifier)
        self.panel.search.setText("Delta")
        self.panel.show_selected()
        self.assertEqual(self.panel.search.text(), "")
        self.assertTrue(group.expanded)
        self.assertFalse(self.panel.rows[a.identifier].isHidden())
        self.assertIs(self.state.selected_object, a)

    def test_keyboard_navigation_uses_display_order_and_expands_groups(self):
        group = self.make_group()
        row = self.panel.group_rows[group.identifier]
        self.panel.select_group(group.identifier)
        self.panel.toggle_group(group.identifier)
        QTest.keyClick(row.name_button, Qt.Key_Right)
        self.assertTrue(group.expanded)
        QTest.keyClick(row.name_button, Qt.Key_Right)
        self.assertIs(self.state.selected_object, self.objects[0])
        first = self.panel.rows[self.objects[0].identifier]
        QTest.keyClick(first.name_button, Qt.Key_Down, Qt.ShiftModifier)
        self.assertEqual(set(self.state.selected_objects), set(self.objects[:2]))
        QTest.keyClick(self.panel.rows[self.objects[1].identifier].name_button, Qt.Key_Left)
        self.assertEqual(self.panel._cursor_key, group.identifier)
        QTest.keyClick(row.name_button, Qt.Key_Left)
        self.assertFalse(group.expanded)

    def test_isolation_is_temporary_respects_hidden_flags_and_has_an_exit_after_delete(self):
        a, b, c, _ = self.objects
        group = self.make_group()
        b.editor_visible = False
        self.state.select_many([a.identifier, b.identifier])
        count = self.state.undo_stack.count()
        # Native accessibility activates a checkable tool button by its state.
        self.panel.isolation_button.setChecked(True)
        self.assertTrue(a.viewport_visible)
        self.assertFalse(b.viewport_visible)
        self.assertFalse(c.viewport_visible)
        self.assertTrue(c.editor_visible)
        self.assertEqual(self.state.undo_stack.count(), count)
        self.state.delete_selected()
        self.assertEqual(self.panel.isolation_button.text(), "Exit Isolation")
        self.assertTrue(self.panel.isolation_button.isEnabled())
        self.panel.isolation_button.click()
        self.assertTrue(c.viewport_visible)
        self.state.undo_stack.undo()
        self.assertFalse(b.viewport_visible)
        self.assertTrue(group.editor_visible)

    def send_drop(self, surface, mime, y=12):
        point = QPoint(60, y)
        enter = QDragEnterEvent(point, Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(surface, enter)
        move = QDragMoveEvent(point, Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(surface, move)
        drop = QDropEvent(QPointF(point), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(surface, drop)
        return enter, move, drop

    def test_native_drop_events_move_multiple_objects_and_display_target_cue(self):
        group = self.make_group(objects=[])
        row = self.panel.group_rows[group.identifier]
        mime = self.panel.drag_mime("object", self.keys(self.objects[:2]))
        enter = QDragEnterEvent(QPoint(60, 12), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(row, enter)
        self.assertTrue(enter.isAccepted())
        self.assertEqual(row.property("dropPosition"), "inside")
        drop = QDropEvent(QPointF(60, 12), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(row, drop)
        self.assertTrue(drop.isAccepted())
        self.assertEqual(group.members, self.keys(self.objects[:2]))
        self.assertEqual(row.property("dropPosition"), "")
        self.state.undo_stack.undo()
        self.assertEqual(group.members, [])

    def test_drop_edges_reorder_root_and_group_members_and_root_drop_ungroups(self):
        a, b, c, d = self.objects
        group = self.make_group()
        self.send_drop(self.panel.rows[a.identifier], self.panel.drag_mime("object", [b.identifier]), 1)
        self.assertEqual(group.members, [b.identifier, a.identifier])
        self.send_drop(self.panel.rows[c.identifier], self.panel.drag_mime("object", [d.identifier]), 1)
        self.assertEqual(self.scene.root_order, [group.identifier, d.identifier, c.identifier])
        self.send_drop(self.panel.scroll.widget(), self.panel.drag_mime("object", [a.identifier]), self.panel.scroll.widget().height() - 2)
        self.assertEqual(group.members, [b.identifier])
        self.assertEqual(self.scene.root_order[-1], a.identifier)
        self.send_drop(self.panel.rows[c.identifier], self.panel.drag_mime("group", [group.identifier]), 23)
        self.assertEqual(self.scene.root_order, [d.identifier, c.identifier, group.identifier, a.identifier])

    def test_drag_rejects_foreign_invalid_nested_and_filtered_moves(self):
        first = self.make_group()
        second = self.make_group("Second", objects=[])
        mime = self.panel.drag_mime("group", [first.identifier])
        enter, _, drop = self.send_drop(self.panel.group_rows[second.identifier], mime)
        self.assertFalse(enter.isAccepted())
        self.assertFalse(drop.isAccepted())
        foreign = QMimeData()
        foreign.setData(self.panel.DRAG_MIME, json.dumps({"scene": "another-scene", "kind": "object",
                                                       "ids": self.keys(self.objects)}).encode())
        self.assertIsNone(self.panel.decode_drag(foreign))
        foreign.setData(self.panel.DRAG_MIME, b'{broken')
        self.assertIsNone(self.panel.decode_drag(foreign))
        self.panel.search.setText("Alpha")
        self.assertIsNone(self.panel.decode_drag(self.panel.drag_mime("object", self.keys(self.objects))))

    def test_malformed_organization_keeps_all_objects_once(self):
        a, b, c, d = self.objects
        first, second = SceneGroup("One"), SceneGroup("Two")
        first.members = [a.identifier, a.identifier, "missing", ["invalid"]]
        second.members = [a.identifier, b.identifier]
        self.state.replace_objects(self.objects, [first, second], [first.identifier, first.identifier, "missing"])
        self.assertEqual(first.members, [a.identifier])
        self.assertEqual(second.members, [b.identifier])
        self.assertEqual(set(self.state.ordered_object_ids()), set(self.keys(self.objects)))
        self.assertEqual(len(self.state.ordered_object_ids()), 4)
        self.assertEqual(len(self.panel.rows), 4)

    def test_drag_source_keeps_multiple_selection_instead_of_clicking_one_row(self):
        a, b = self.objects[:2]
        self.state.select_many([a.identifier, b.identifier])
        button = self.panel.rows[a.identifier].name_button
        with patch("simuo.ui.panels.hierarchy.panel.QDrag") as drag:
            QTest.mousePress(button, Qt.LeftButton, pos=QPoint(2, 10))
            move = QMouseEvent(QEvent.Type.MouseMove, QPointF(80, 10), QPointF(80, 10),
                               Qt.NoButton, Qt.LeftButton, Qt.NoModifier)
            QApplication.sendEvent(button, move)
            drag.return_value.exec.assert_called_once_with(Qt.MoveAction)
            mime = drag.return_value.setMimeData.call_args.args[0]
            self.assertEqual(self.panel.decode_drag(mime), ("object", [a.identifier, b.identifier]))
            QTest.mouseRelease(button, Qt.LeftButton)
        self.assertEqual(self.state.selected_objects, (a, b))
