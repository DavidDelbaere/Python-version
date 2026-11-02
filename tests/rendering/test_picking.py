"""Check exact mesh picking, transformed objects, and viewport mouse input."""

from types import SimpleNamespace
import unittest

import glm
import numpy as np
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from tests.support.paths import ROOT
from tests.support.qt import get_application

from simuo.rendering.picking import PickMesh, pick_object
from simuo.rendering.camera import Camera
from simuo.rendering.viewport import OpenGLViewport
from simuo.rendering.meshes import load_obj_flat_shaded
from simuo.scene.model import SceneObject


class PickingGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mesh = PickMesh(load_obj_flat_shaded(ROOT / "Assets/cube.simuOPart"))

    def rendered(self, obj):
        return {"SceneObject": obj, "pick_mesh": self.mesh}

    def test_closest_mesh_wins_regardless_of_scene_order(self):
        far, near = SceneObject("Far"), SceneObject("Near")
        near.position[2] = 4.0
        result = pick_object([self.rendered(far), self.rendered(near)], (0, 0, 10), (0, 0, -1))
        self.assertIs(result, near)

    def test_hidden_and_selection_locked_objects_are_not_pickable(self):
        near, far = SceneObject("Near"), SceneObject("Far")
        near.position[2] = 4
        rendered = [self.rendered(near), self.rendered(far)]
        near.editor_visible = False
        self.assertIs(pick_object(rendered, (0, 0, 10), (0, 0, -1)), far)
        near.editor_visible = True
        near.selection_locked = True
        self.assertIs(pick_object(rendered, (0, 0, 10), (0, 0, -1)), far)
        near.selection_locked = False
        self.assertIs(pick_object(rendered, (0, 0, 10), (0, 0, -1)), near)

    def test_miss_and_objects_behind_camera_or_outside_clip_planes(self):
        obj = SceneObject()
        rendered = [self.rendered(obj)]
        self.assertIsNone(pick_object(rendered, (5, 5, 10), (0, 0, -1)))
        self.assertIsNone(pick_object(rendered, (0, 0, 10), (0, 0, 1)))
        self.assertIsNone(pick_object(rendered, (0, 0, 10), (0, 0, -1), 0.0, 8.9))
        self.assertIsNone(pick_object(rendered, (0, 0, 10), (0, 0, -1), 11.1, 1000))

    def test_empty_part_of_mesh_bounds_is_not_a_hit(self):
        vertices = np.zeros((3, 6), dtype=np.float32)
        vertices[:, :3] = [(-1, -1, 0), (1, -1, 0), (-1, 1, 0)]
        obj = SceneObject()
        rendered = [{"SceneObject": obj, "pick_mesh": PickMesh(vertices)}]
        self.assertIsNone(pick_object(rendered, (0.9, 0.9, 10), (0, 0, -1)))
        self.assertIs(pick_object(rendered, (-0.5, -0.5, 10), (0, 0, -1)), obj)

    def test_picking_tracks_live_translation_rotation_and_nonuniform_scale(self):
        obj = SceneObject()
        obj.position = [4.0, 0.0, 0.0]
        obj.rotation = [0.0, 0.0, 90.0]
        obj.scale = [3.0, 0.5, 0.5]
        rendered = [self.rendered(obj)]
        self.assertIs(pick_object(rendered, (4, 2, 10), (0, 0, -1)), obj)
        self.assertIsNone(pick_object(rendered, (6, 0, 10), (0, 0, -1)))
        obj.position[0] = -4.0
        self.assertIsNone(pick_object(rendered, (4, 2, 10), (0, 0, -1)))
        self.assertIs(pick_object(rendered, (-4, 2, 10), (0, 0, -1)), obj)

    def test_negative_tiny_and_zero_scale(self):
        obj = SceneObject()
        for scale in ((-2.0, 0.5, -0.5), (0.001, 0.001, 0.001)):
            obj.scale = list(scale)
            self.assertIs(pick_object([self.rendered(obj)], (0, 0, 10), (0, 0, -1)), obj)
        obj.scale = [0.0, 1.0, 1.0]
        self.assertIsNone(pick_object([self.rendered(obj)], (0, 0, 10), (0, 0, -1)))

    def test_world_distance_order_survives_different_scales(self):
        near, far = SceneObject("Near"), SceneObject("Far")
        near.position[2] = 5.0
        near.scale = [0.1, 0.1, 0.1]
        far.scale = [2.0, 2.0, 2.0]
        self.assertIs(pick_object([self.rendered(far), self.rendered(near)], (0, 0, 10), (0, 0, -1)), near)

    def test_empty_mesh_and_degenerate_faces_are_ignored(self):
        obj = SceneObject()
        for vertices in (np.array([], dtype=np.float32), np.zeros(18, dtype=np.float32)):
            rendered = [{"SceneObject": obj, "pick_mesh": PickMesh(vertices)}]
            self.assertIsNone(pick_object(rendered, (0, 0, 10), (0, 0, -1)))

    def test_unprojection_matches_rendered_position_after_camera_movement_and_resize(self):
        camera = Camera()
        camera.position = glm.vec3(3, 2, 10)
        camera.yaw, camera.pitch = -115.0, -12.0
        camera.update_vectors()
        target = glm.vec3(-4, -1, -5)
        for width, height in ((800, 600), (1400, 500), (500, 900)):
            projection = glm.perspective(glm.radians(60.0), width / height, 0.1, 1000.0)
            clip = projection * camera.view_matrix() * glm.vec4(target, 1.0)
            ndc = clip / clip.w
            point = QPointF((ndc.x + 1) * width / 2, (1 - ndc.y) * height / 2)
            event = SimpleNamespace(position=lambda: point)
            origin, direction = camera.mouse_ray(event, width, height, projection, camera.view_matrix())
            expected = glm.normalize(target - camera.position)
            self.assertLess(glm.length(direction - expected), 1e-4)
            self.assertLess(glm.length(origin - camera.position), 1e-6)


class ViewportClicks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_application()

    def test_click_emits_object_id_and_empty_click_clears_without_debug_ray(self):
        viewport = OpenGLViewport()
        self.addCleanup(viewport.close)
        viewport.timer.stop()
        viewport.resize(800, 600)
        viewport.camera.position = glm.vec3(0, 0, 10)
        obj = SceneObject("Cube")
        viewport.renderObjects = [{
            "SceneObject": obj,
            "pick_mesh": PickMesh(load_obj_flat_shaded(ROOT / "Assets/cube.simuOPart")),
        }]
        selected = []
        viewport.object_picked.connect(selected.append)
        for point in (QPointF(400, 300), QPointF(1, 1)):
            event = QMouseEvent(QEvent.Type.MouseButtonPress, point, point, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            QApplication.sendEvent(viewport, event)
        self.assertEqual(selected, [obj.identifier, None])
        self.assertIsNone(viewport.debug_ray)
        viewport.right_mouse_down = True
        QApplication.sendEvent(viewport, event)
        viewport.right_mouse_down = False
        self.assertEqual(len(selected), 2)

    def test_framing_fits_transformed_meshes_at_different_viewport_aspects(self):
        from itertools import product
        from simuo.rendering.picking import object_matrix

        viewport = OpenGLViewport()
        self.addCleanup(viewport.close)
        viewport.timer.stop()
        obj = SceneObject("Framed")
        obj.position = [17, -4, -25]
        obj.rotation = [20, 45, -15]
        obj.scale = [-3, 0.5, 2]
        mesh = PickMesh(load_obj_flat_shaded(ROOT / "Assets/cube.simuOPart"))
        viewport.renderObjects = [{"SceneObject": obj, "pick_mesh": mesh}]
        viewport.camera.yaw, viewport.camera.pitch = -110, 15
        viewport.camera.update_vectors()
        orientation = viewport.camera.yaw, viewport.camera.pitch
        for width, height in ((900, 300), (300, 900)):
            viewport.resize(width, height)
            self.assertTrue(viewport.frame_object(obj))
            camera = viewport.camera
            projection = glm.perspective(glm.radians(camera.field_of_view), width / height,
                                         camera.near_plane, camera.far_plane)
            matrix = projection * camera.view_matrix() * object_matrix(obj)
            for x, y, z in product((-1, 1), repeat=3):
                clip = matrix * glm.vec4(x, y, z, 1)
                ndc = clip / clip.w
                self.assertLessEqual(abs(ndc.x), 0.9)
                self.assertLessEqual(abs(ndc.y), 0.9)
                self.assertLessEqual(abs(ndc.z), 1.0)
            self.assertEqual((camera.yaw, camera.pitch), orientation)
        obj.editor_visible = False
        position = glm.vec3(viewport.camera.position)
        self.assertFalse(viewport.frame_object(obj))
        self.assertEqual(viewport.camera.position, position)

    def test_framing_multiple_objects_fits_the_combined_bounds(self):
        viewport = OpenGLViewport()
        self.addCleanup(viewport.close)
        viewport.timer.stop()
        a, b = SceneObject("A"), SceneObject("B")
        a.position, b.position = [-20, 4, 10], [30, -6, -15]
        mesh = PickMesh(load_obj_flat_shaded(ROOT / "Assets/cube.simuOPart"))
        viewport.renderObjects = [{"SceneObject": obj, "pick_mesh": mesh} for obj in (a, b)]
        viewport.resize(300, 800)
        self.assertTrue(viewport.frame_object((a, b)))
        camera = viewport.camera
        projection = glm.perspective(glm.radians(camera.field_of_view), 300 / 800,
                                     camera.near_plane, camera.far_plane)
        from itertools import product
        from simuo.rendering.picking import object_matrix
        for obj in (a, b):
            matrix = projection * camera.view_matrix() * object_matrix(obj)
            for corner in product((-1, 1), repeat=3):
                clip = matrix * glm.vec4(*corner, 1)
                self.assertLessEqual(abs(clip.x / clip.w), 0.9)
                self.assertLessEqual(abs(clip.y / clip.w), 0.9)

    def test_escape_delegates_to_editor_without_becoming_a_camera_movement_key(self):
        from PySide6.QtTest import QTest

        viewport = OpenGLViewport()
        self.addCleanup(viewport.close)
        viewport.timer.stop()
        escapes = []
        viewport.escape_requested.connect(lambda: escapes.append(True))
        QTest.keyClick(viewport, Qt.Key_Escape)
        self.assertEqual(escapes, [True])
        self.assertNotIn(Qt.Key_Escape, viewport.keys)


if __name__ == "__main__":
    unittest.main()
