"""Camera motion and editor selection/shortcut input must not interfere."""

import unittest

import glm
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication

from tests.support.paths import ROOT
from tests.support.qt import get_application
from simuo.editor.state import EditorState
from simuo.rendering.meshes import load_obj_flat_shaded
from simuo.rendering.picking import PickMesh
from simuo.rendering.viewport import OpenGLViewport
from simuo.scene.model import Scene, SceneObject


class CameraInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()
        cls.mesh = PickMesh(load_obj_flat_shaded(ROOT / 'Assets/cube.simuOPart'))

    def setUp(self):
        self.scene = Scene()
        self.objects = [SceneObject('Left'), SceneObject('Right')]
        for obj, x in zip(self.objects, (-2, 2)):
            obj.position[0] = x
            self.scene.addObject(obj)
        self.state = EditorState(self.scene)
        self.viewport = OpenGLViewport(scene=self.scene)
        self.viewport.timer.stop()
        self.addCleanup(self.viewport.close)
        self.viewport.resize(800, 600)
        self.viewport.camera.position = glm.vec3(0, 0, 10)
        self.viewport.renderObjects = [{'SceneObject': obj, 'pick_mesh': self.mesh} for obj in self.objects]
        self.viewport.object_picked.connect(
            lambda key: self.state.select_from_viewport(key, self.viewport.pick_modifiers)
        )

    def key(self, key, modifiers=Qt.NoModifier, release=False, repeat=False):
        event = QKeyEvent(QEvent.Type.KeyRelease if release else QEvent.Type.KeyPress,
                          key, modifiers, '', repeat, 1)
        QApplication.sendEvent(self.viewport, event)

    def click(self, obj, modifiers):
        camera = self.viewport.camera
        projection = glm.perspective(glm.radians(camera.field_of_view), 800 / 600,
                                     camera.near_plane, camera.far_plane)
        clip = projection * camera.view_matrix() * glm.vec4(*obj.position, 1)
        point = QPointF((clip.x / clip.w + 1) * 400, (1 - clip.y / clip.w) * 300)
        for event_type in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
            event = QMouseEvent(event_type, point, point, Qt.LeftButton,
                                Qt.LeftButton if event_type == QEvent.Type.MouseButtonPress else Qt.NoButton,
                                modifiers)
            QApplication.sendEvent(self.viewport, event)

    def test_command_control_click_toggles_selection_without_camera_drift(self):
        for key, modifier in ((Qt.Key_Control, Qt.ControlModifier), (Qt.Key_Meta, Qt.MetaModifier)):
            with self.subTest(modifier=modifier):
                self.state.select(None)
                before = glm.vec3(self.viewport.camera.position)
                self.key(key, modifier)
                self.viewport.update_camera(0.5)  # Holding the modifier before clicking.
                self.click(self.objects[0], modifier)
                self.viewport.update_camera(0.5)
                self.click(self.objects[1], modifier)
                self.viewport.update_camera(0.5)
                self.assertEqual(self.state.selected_objects, tuple(self.objects))
                self.click(self.objects[0], modifier)
                self.assertEqual(self.state.selected_objects, (self.objects[1],))
                self.key(key, release=True)
                self.viewport.update_camera(0.5)
                self.assertEqual(self.viewport.camera.position, before)
                self.assertFalse(self.viewport.keys)
                self.assertFalse(self.scene.dirty)

    def test_shortcut_letters_do_not_start_motion_even_after_modifier_release(self):
        for key, modifier in ((Qt.Key_Control, Qt.ControlModifier), (Qt.Key_Meta, Qt.MetaModifier),
                              (Qt.Key_Alt, Qt.AltModifier)):
            before = glm.vec3(self.viewport.camera.position)
            self.key(key, modifier)
            for letter in (Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D, Qt.Key_C, Qt.Key_Space):
                self.key(letter, modifier)
                self.viewport.update_camera(0.2)
            self.key(key, release=True)
            self.key(Qt.Key_D, repeat=True)
            self.viewport.update_camera(0.2)
            self.assertEqual(self.viewport.camera.position, before)
            self.assertFalse(self.viewport.keys)

    def test_modifier_press_and_modified_click_stop_preexisting_camera_input(self):
        for interrupt in (lambda: self.key(Qt.Key_Control, Qt.ControlModifier),
                          lambda: self.click(self.objects[0], Qt.ControlModifier)):
            self.key(Qt.Key_W)
            self.viewport.update_camera(0.1)
            before = glm.vec3(self.viewport.camera.position)
            interrupt()
            self.viewport.update_camera(0.5)
            self.assertEqual(self.viewport.camera.position, before)
            self.assertFalse(self.viewport.keys)
            self.key(Qt.Key_Control, release=True)
            self.key(Qt.Key_W, release=True)

    def test_space_and_c_move_vertically_and_autorepeat_release_does_not_stop_motion(self):
        before = glm.vec3(self.viewport.camera.position)
        self.key(Qt.Key_Space)
        self.viewport.update_camera(0.1)
        self.assertAlmostEqual(self.viewport.camera.position.y, before.y + 1)
        self.key(Qt.Key_Space, release=True)
        self.key(Qt.Key_C)
        self.key(Qt.Key_C, release=True, repeat=True)
        self.viewport.update_camera(0.1)
        self.assertEqual(self.viewport.camera.position, before)
        self.key(Qt.Key_C, release=True)
        self.viewport.update_camera(0.5)
        self.assertEqual(self.viewport.camera.position, before)

    def test_framing_keys_are_scoped_and_never_arm_camera_movement(self):
        frames, scenes = [], []
        self.viewport.frame_requested.connect(lambda: frames.append(True))
        self.viewport.frame_scene_requested.connect(lambda: scenes.append(True))
        self.key(Qt.Key_F)
        self.key(Qt.Key_F, Qt.ShiftModifier)
        self.key(Qt.Key_F, Qt.ControlModifier)
        self.assertEqual(frames, [True])
        self.assertEqual(scenes, [True])
        self.assertFalse(self.viewport.keys)
