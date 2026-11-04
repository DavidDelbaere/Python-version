"""Feature tree, 3D viewing, plane/face sketching and additive extrusions."""
import copy
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QPen, QPolygonF
from PySide6.QtWidgets import (QDockWidget, QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QCheckBox, QDialogButtonBox,
    QMessageBox, QFileDialog, QToolBar, QLabel)

from part_editor import PartEditor
from part_viewport import PartViewport
from feature_document import new_feature_document,open_feature_document,save_feature_document
from feature_geometry import FeatureModel,PLANES,support_frame,to_plane
from part_export import export_vertices
from sketch_geometry import Sketch


class FeaturePartEditor(PartEditor):
    def __init__(self,path=None):
        self.model = None
        self.active_id = None
        self.selected_support = {"type":"plane","name":"Front"}
        self.sketch_plane_label = "Front Plane (XY)"
        super().__init__()
        self.data,self.model = new_feature_document()
        self.stack = QStackedWidget()
        self.viewport = PartViewport(self)
        self.viewport.face_selected.connect(self.select_face)
        self.viewport.plane_selected.connect(self.select_plane)
        self.centralWidget().layout().removeWidget(self.canvas)
        self.canvas.setParent(None)
        self.stack.addWidget(self.viewport)
        self.stack.addWidget(self.canvas)
        self.centralWidget().layout().addWidget(self.stack)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Part hierarchy")
        self.tree.setMinimumWidth(140)
        self.tree.itemClicked.connect(self.tree_clicked)
        self.tree.itemDoubleClicked.connect(self.tree_double_clicked)
        self.hierarchyDock = QDockWidget("Feature tree",self)
        self.hierarchyDock.setWidget(self.tree)
        self.addDockWidget(Qt.LeftDockWidgetArea,self.hierarchyDock)
        self.resizeDocks([self.hierarchyDock],[180],Qt.Horizontal)
        toolbar = QToolBar("Features",self)
        self.addToolBar(Qt.TopToolBarArea,toolbar)
        menu = self.menuBar().addMenu("Features")
        self.feature_actions = {}
        for name,callback in [("3D View",self.view_model),("New Sketch",self.new_sketch),
                              ("Extrude…",self.extrude_dialog),("Finish Sketch",self.finish_sketch),
                              ("Edit Sketch",self.edit_sketch)]:
            action = QAction(name,self)
            action.setToolTip(name+" on the selected reference plane, sketch or face")
            action.triggered.connect(callback)
            menu.addAction(action)
            toolbar.addAction(action)
            self.feature_actions[name] = action
        menu.addSeparator()
        for name, callback in (("Delete Sketch…", self.delete_sketch), ("Delete Extrusion…", self.delete_extrusion)):
            action = QAction(name, self)
            action.triggered.connect(callback)
            menu.addAction(action)
            self.feature_actions[name] = action
        delete_feature = QAction("Delete selected sketch / extrusion…", self)
        delete_feature.setShortcuts(["Backspace", "Delete"])
        delete_feature.setShortcutContext(Qt.WidgetShortcut)
        delete_feature.setAutoRepeat(False)
        delete_feature.triggered.connect(self.delete_tree_item)
        self.tree.addAction(delete_feature)
        self.tree.setContextMenuPolicy(Qt.ActionsContextMenu)
        view_menu = next(action.menu() for action in self.menuBar().actions() if action.text()=="View")
        view_menu.addAction(self.hierarchyDock.toggleViewAction())
        for action in view_menu.actions():
            if action.shortcut().toString()=="F":
                action.setText("Frame view")
                action.triggered.disconnect()
                action.triggered.connect(self.frame_view)
        self.select_mode()
        for label in self.findChildren(QLabel):
            if label.text()=="Thickness:":
                label.setText("Next extrusion:")
        self.refresh()
        self.viewport.fit()
        if path:
            self.open_path(path)

    @property
    def active_feature(self):
        return next((f for f in self.model.features if f["id"]==self.active_id),None) if self.model else None

    def snapshot(self):
        return (self.model.geometry(),self.active_id,copy.deepcopy(self.selected_support))

    def restore(self,state):
        self.model = FeatureModel.from_geometry(state[0])
        self.active_id,self.selected_support = state[1],copy.deepcopy(state[2])
        self.bind_active()
        self.refresh()

    def accept_model(self,candidate,active_id=None):
        candidate.build()
        self.history.append(self.snapshot())
        self.future.clear()
        self.model = candidate
        if active_id is not None:
            self.active_id = active_id
        self.dirty = True
        self.bind_active()
        self.refresh()

    def bind_active(self):
        feature = self.active_feature
        self.sketch = Sketch.from_geometry(feature["sketch"]) if feature else Sketch()
        if feature:
            support = feature["support"]
            self.sketch_plane_label = support.get("name",support.get("label","Face"))+" sketch · mm"

    def refresh(self,rebuild=True):
        super().refresh()
        if self.model is None or not hasattr(self,"tree"):
            return
        self.viewport.model = self.model
        self.viewport.active_id = self.active_id
        self.viewport.support = self.selected_support
        self.viewport.update()
        if rebuild:
            self.rebuild_tree()
        feature = self.active_feature
        text = f"{len(self.model.features)} sketches · {len(self.model.faces)} solid faces"
        if self.model.has_solid:
            text += f"\nVolume: {self.model.volume*1e9:.3f} mm³"
        if feature:
            support = feature["support"]
            text += "\n"+feature["name"]+" on "+support.get("name",support.get("label","Face"))
            text += "\n"+("Closed sketch — ready to extrude" if self.sketch.closed else "Open sketch")
            if feature["depth"] is not None:
                text += f"\nExtruded {feature['depth']*1000:g} mm"
        else:
            text += "\nSelect a plane or a model face, then New Sketch."
        self.summary.setText(text)
        self.statusBar().showMessage("Plane or face → New Sketch → draw/dimension → Finish Sketch → Extrude. Drag in 3D to orbit.")

    def rebuild_tree(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        planes = QTreeWidgetItem(self.tree,["Reference planes"])
        for name in PLANES:
            item = QTreeWidgetItem(planes,[name+" Plane"])
            item.setData(0,Qt.UserRole,("plane",name))
        features = QTreeWidgetItem(self.tree,["Sketches and extrusions"])
        for i,feature in enumerate(self.model.features):
            support = feature["support"]
            parent = QTreeWidgetItem(features,[feature["name"]+" · "+support.get("name",support.get("label","Face"))])
            parent.setData(0,Qt.UserRole,("feature",feature["id"]))
            if feature["id"]==self.active_id:
                self.tree.setCurrentItem(parent)
            if feature["depth"] is not None:
                item = QTreeWidgetItem(parent,[f"Extrude {i+1} · {feature['depth']*1000:g} mm"])
                item.setData(0,Qt.UserRole,("extrusion",feature["id"]))
        faces = QTreeWidgetItem(self.tree,["Solid faces"])
        for i,face in enumerate(self.model.faces):
            item = QTreeWidgetItem(faces,[face["label"]])
            item.setData(0,Qt.UserRole,("face",i))
            item.setToolTip(0,"Select this flat face, then New Sketch")
        planes.setExpanded(True)
        features.setExpanded(True)
        self.tree.blockSignals(False)

    def tree_clicked(self,item,column=0):
        value = item.data(0,Qt.UserRole)
        if not value:
            return
        if value[0]=="plane":
            self.selected_support = {"type":"plane","name":value[1]}
            self.viewport.selected_face = -1
            self.view_model()
        elif value[0]=="face":
            self.view_model()
            self.select_face(value[1])
        else:
            self.active_id = value[1]
            self.bind_active()
            self.viewport.selected_face = -1
            self.selected_support = copy.deepcopy(self.active_feature["support"])
        self.refresh(rebuild=False)

    def tree_double_clicked(self,item,column=0):
        value = item.data(0,Qt.UserRole)
        if value and value[0] in ("feature", "extrusion"):
            self.active_id = value[1]
            self.edit_sketch()
        elif value and value[0] in ("plane","face"):
            self.tree_clicked(item)
            self.new_sketch()

    def select_plane(self,name):
        planes = self.tree.topLevelItem(0)
        if planes is None:
            return
        for index in range(planes.childCount()):
            item = planes.child(index)
            if item.data(0,Qt.UserRole)==("plane",name):
                self.tree.setCurrentItem(item)
                self.tree_clicked(item)
                self.statusBar().showMessage(f"{name} Plane selected — choose New Sketch to draw on it.")
                break

    def select_face(self,index):
        if not 0<=index<len(self.model.faces):
            return
        self.selected_support = self.model.face_support(index)
        self.viewport.selected_face = index
        self.viewport.support = self.selected_support
        self.viewport.update()
        faces = self.tree.topLevelItem(2)
        if faces is not None and index<faces.childCount():
            faces.setExpanded(True)
            self.tree.setCurrentItem(faces.child(index))
        self.statusBar().showMessage(f"{self.model.faces[index]['label']} selected — choose New Sketch to draw on this face.")

    def new_sketch(self):
        try:
            candidate = FeatureModel(self.model.features)
            feature = candidate.new_sketch(self.selected_support)
            self.accept_model(candidate,feature["id"])
            self.viewport.selected_face = -1
            self.edit_sketch()
        except (ValueError,RuntimeError) as error:
            QMessageBox.warning(self,"Cannot Create Sketch",str(error))

    def edit_sketch(self):
        if self.active_feature is None:
            self.new_sketch()
            return
        self.bind_active()
        self.stack.setCurrentWidget(self.canvas)
        self.line_action.setChecked(not self.sketch.closed)
        self.refresh()
        self.canvas.fit()

    def finish_sketch(self):
        self.select_mode()
        self.view_model()
        self.viewport.fit()

    def view_model(self):
        self.select_mode()
        self.stack.setCurrentWidget(self.viewport)
        self.viewport.update()

    def frame_view(self):
        self.viewport.fit() if self.stack.currentWidget() is self.viewport else self.canvas.fit()

    def set_drawing(self,value):
        super().set_drawing(value)
        if value and self.model is not None and hasattr(self,"stack"):
            if self.active_feature is None:
                self.new_sketch()
            else:
                self.stack.setCurrentWidget(self.canvas)

    def set_arcs(self,value):
        super().set_arcs(value)
        if value and self.model is not None and hasattr(self,"stack"):
            if self.active_feature is None:
                self.new_sketch()
                self.arc_action.setChecked(True)
            else:
                self.stack.setCurrentWidget(self.canvas)

    def set_circles(self,value):
        super().set_circles(value)
        if value and self.model is not None and hasattr(self,"stack"):
            if self.active_feature is None or self.sketch.points:
                self.new_sketch()
                self.circle_action.setChecked(True)
            else:
                self.stack.setCurrentWidget(self.canvas)

    def commit(self,candidate):
        if self.model is None:
            return super().commit(candidate)
        if self.active_feature is None:
            raise ValueError("Choose a plane or face and create a sketch first")
        candidate.validate()
        model = FeatureModel(self.model.features)
        feature = next(f for f in model.features if f["id"]==self.active_id)
        feature["sketch"] = candidate.geometry()
        self.accept_model(model)
        if candidate.closed:
            self.select_mode()

    def change_thickness(self,value):
        if self.model is not None and self.active_feature is not None:
            candidate = copy.deepcopy(self.sketch)
            candidate.thickness = value/1000
            self.commit(candidate)
        self.statusBar().showMessage(f"Next extrusion distance: {value:g} mm")

    def dependent_features(self, roots):
        removed = set(roots)
        while True:
            dependent = {f["id"] for f in self.model.features
                         if f["support"]["type"] == "face" and f["support"]["parent"] in removed}
            if dependent <= removed:
                return removed - set(roots)
            removed.update(dependent)

    def confirm_feature_deletion(self, message, dependent):
        if dependent:
            names = [f["name"] for f in self.model.features if f["id"] in dependent]
            message += "\n\nThese sketches depend on its faces and will also be deleted:\n" + "\n".join(names)
        return QMessageBox.question(
            self, "Delete Sketch / Extrusion", message + "\n\nYou can undo this change.",
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel,
        ) == QMessageBox.Yes

    def accept_deletion(self, candidate, active_id=None):
        self.accept_model(candidate, active_id)
        if self.active_feature is None:
            self.active_id = self.model.features[-1]["id"] if self.model.features else None
        self.selected_support = copy.deepcopy(self.active_feature["support"]) if self.active_feature else {"type":"plane", "name":"Front"}
        self.viewport.selected_face = -1
        self.canvas.selection = -1
        self.bind_active()
        self.select_mode()
        self.refresh()

    def delete_selected_segment(self):
        if self.model is None:
            return super().delete_selected_segment()
        if self.active_feature is None or not 0 <= self.canvas.selection < len(self.sketch.edges):
            self.statusBar().showMessage("Select a sketch line or arc to delete.", 5000)
            return
        try:
            pieces = self.sketch.without_segment(self.canvas.selection)
            root = self.active_id
            dependent = self.dependent_features({root})
            if self.active_feature["depth"] is not None:
                if not self.confirm_feature_deletion("Deleting this segment opens the sketch and removes its extrusion.", dependent):
                    return
            candidate = FeatureModel([f for f in self.model.features if f["id"] not in dependent])
            feature = next(f for f in candidate.features if f["id"] == root)
            feature["sketch"], feature["depth"], feature["symmetric"] = pieces[0].geometry(), None, False
            for number, piece in enumerate(pieces[1:], 2):
                extra = candidate.new_sketch(feature["support"])
                extra["name"] = feature["name"] + f" (section {number})"
                extra["sketch"] = piece.geometry()
            self.accept_deletion(candidate, root)
            self.stack.setCurrentWidget(self.canvas)
            self.statusBar().showMessage("Segment deleted. The remaining outline is open; Ctrl+Z restores it.", 7000)
        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(self, "Cannot Delete Segment", str(error))

    def selected_tree_feature(self):
        item = self.tree.currentItem()
        value = item.data(0, Qt.UserRole) if item else None
        if value and value[0] in ("feature", "extrusion"):
            return next((f for f in self.model.features if f["id"] == value[1]), None)
        self.statusBar().showMessage("Select a sketch or extrusion in the feature tree first.", 5000)
        return None

    def delete_tree_item(self):
        item = self.tree.currentItem()
        value = item.data(0, Qt.UserRole) if item else None
        if value and value[0] == "extrusion":
            self.delete_extrusion()
        elif value and value[0] == "feature":
            self.delete_sketch()

    def delete_sketch(self):
        feature = self.selected_tree_feature()
        if feature is None:
            return
        root = feature["id"]
        dependent = self.dependent_features({root})
        description = feature["name"] + (" and its extrusion" if feature["depth"] is not None else "")
        if not self.confirm_feature_deletion(f"Delete {description}?", dependent):
            return
        candidate = FeatureModel([f for f in self.model.features if f["id"] not in dependent | {root}])
        try:
            self.accept_deletion(candidate)
            self.view_model()
        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(self, "Cannot Delete Sketch", str(error))

    def delete_extrusion(self):
        feature = self.selected_tree_feature()
        if feature is None or feature["depth"] is None:
            self.statusBar().showMessage("Select an extruded sketch or extrusion first.", 5000)
            return
        root = feature["id"]
        dependent = self.dependent_features({root})
        if not self.confirm_feature_deletion(f"Delete the extrusion of {feature['name']}? The sketch will be kept.", dependent):
            return
        candidate = FeatureModel([f for f in self.model.features if f["id"] not in dependent])
        kept = next(f for f in candidate.features if f["id"] == root)
        kept["depth"], kept["symmetric"] = None, False
        try:
            self.accept_deletion(candidate, root)
            self.view_model()
        except (ValueError, RuntimeError) as error:
            QMessageBox.warning(self, "Cannot Delete Extrusion", str(error))

    def extrude_face(self,index,distance,symmetric=False):
        candidate = FeatureModel(self.model.features).build()
        sketch,support = candidate.face_sketch(index),candidate.face_support(index)
        feature = candidate.new_sketch(support)
        feature["name"] = f"Face extrusion {len(candidate.features)}"
        feature["sketch"] = sketch.geometry()
        feature["depth"],feature["symmetric"] = float(distance),bool(symmetric)
        self.accept_model(candidate,feature["id"])
        self.viewport.selected_face = -1
        self.view_model()
        self.viewport.fit()

    def extrude_active(self,distance,symmetric=False):
        if self.active_feature is None or not self.sketch.closed:
            raise ValueError("Create and close a sketch before extruding it")
        candidate = FeatureModel(self.model.features)
        feature = next(f for f in candidate.features if f["id"]==self.active_id)
        feature["depth"],feature["symmetric"] = float(distance),bool(symmetric)
        self.accept_model(candidate)
        self.view_model()
        self.viewport.selected_face = -1
        self.viewport.fit()

    def extrude_dialog(self):
        direct_face = self.viewport.selected_face if self.stack.currentWidget() is self.viewport else -1
        if direct_face<0 and (self.active_feature is None or not self.sketch.closed):
            QMessageBox.information(self,"Extrude Sketch","Select a closed sketch in the tree, or create one on a plane or face first.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Extrude Face")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        distance = QDoubleSpinBox()
        distance.setObjectName("extrudeDistance")
        distance.setRange(.001,1e6)
        distance.setDecimals(3)
        distance.setSuffix(" mm")
        depth = self.active_feature["depth"] if direct_face<0 else None
        distance.setValue(abs(depth)*1000 if depth is not None else self.thickness.value())
        reverse = QCheckBox("Reverse direction")
        reverse.setChecked(depth is not None and depth<0)
        symmetric = QCheckBox("Symmetric about sketch plane")
        symmetric.setChecked(self.active_feature["symmetric"] if direct_face<0 else False)
        form.addRow("Distance:",distance)
        layout.addLayout(form)
        layout.addWidget(reverse)
        layout.addWidget(symmetric)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec()==QDialog.Accepted:
            try:
                method = self.extrude_active if direct_face<0 else lambda d,s: self.extrude_face(direct_face,d,s)
                method(distance.value()/1000*(-1 if reverse.isChecked() else 1),symmetric.isChecked())
            except (ValueError,RuntimeError) as error:
                QMessageBox.warning(self,"Cannot Extrude",str(error))

    def undo(self):
        if self.history:
            self.future.append(self.snapshot())
            self.restore(self.history.pop())
            self.dirty = True
            self.refresh()

    def redo(self):
        if self.future:
            self.history.append(self.snapshot())
            self.restore(self.future.pop())
            self.dirty = True
            self.refresh()

    def sketch_context_geometry(self):
        """Project the solid before the active sketch into its drawing frame."""
        feature = self.active_feature
        if not feature:
            return [], []
        cache = getattr(self, "_sketch_context_cache", None)
        if cache is not None and cache[:2] == (self.model, self.active_id):
            return cache[2]
        index = self.model.features.index(feature)
        context = FeatureModel(self.model.features[:index]).build()
        frame = support_frame(feature["support"])
        normal = np.cross(frame["u"],frame["v"])
        triangles, edges = [], []
        for face in context.faces:
            # Only faces pointing toward the sketch viewer have projected area.
            if np.dot(face["normal"], normal) <= 1e-7:
                continue
            triangles.extend(to_plane(face["triangles"], frame))
            edges.extend(to_plane(edge, frame) for edge in face["edges"])
        result = (triangles, edges)
        self._sketch_context_cache = (self.model, self.active_id, result)
        return result

    def sketch_context_points(self):
        triangles, _ = self.sketch_context_geometry()
        return [point for triangle in triangles for point in triangle]

    def paint_sketch_context(self,painter,canvas):
        triangles, edges = self.sketch_context_geometry()
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#454c54"))
        for triangle in triangles:
            painter.drawPolygon(QPolygonF([canvas.screen(point) for point in triangle]))
        painter.setPen(QPen(QColor("#89939d"), 1))
        for a, b in edges:
            painter.drawLine(canvas.screen(a), canvas.screen(b))
        painter.restore()

    def new_part(self):
        if self.confirm_changes():
            self.data,self.model = new_feature_document()
            self.active_id,self.path,self.dirty = None,None,False
            self.selected_support = {"type":"plane","name":"Front"}
            self.history.clear()
            self.future.clear()
            self.bind_active()
            self.name.setText(self.data["name"])
            self.select_mode()
            self.view_model()
            self.refresh()
            self.viewport.fit()

    def open_path(self,path):
        try:
            data,model = open_feature_document(path)
        except (OSError,ValueError,TypeError,RuntimeError,ImportError) as error:
            QMessageBox.warning(self,"Cannot Open Part",f"{error}\nOpen a JSON box, sketch part or feature part. Legacy OBJ meshes have no editable features.")
            return False
        self.data,self.model,self.path = data,model,Path(path)
        self.active_id = model.features[-1]["id"] if model.features else None
        self.selected_support = copy.deepcopy(self.active_feature["support"]) if self.active_feature else {"type":"plane","name":"Front"}
        self.dirty = False
        self.history.clear()
        self.future.clear()
        self.bind_active()
        self.name.setText(data["name"])
        self.select_mode()
        self.view_model()
        self.refresh()
        self.viewport.fit()
        return True

    def _save_to(self,path):
        try:
            data = save_feature_document(path,self.data,self.model)
        except (OSError,ValueError,RuntimeError) as error:
            QMessageBox.warning(self,"Cannot Save Part",str(error))
            return False
        self.data,self.path,self.dirty = data,Path(path),False
        self.refresh()
        return True

    def export_mesh(self,kind):
        if not self.model.has_solid:
            QMessageBox.information(self,"Export Part","Extrude a closed sketch before exporting the 3D solid.")
            return False
        path,_ = QFileDialog.getSaveFileName(self,f"Export {kind.upper()}",str((self.path or Path("part.simuOPart")).with_suffix("."+kind)),f"{kind.upper()} Mesh (*.{kind})")
        if not path:
            return False
        path = Path(path)
        if path.suffix.lower()!="."+kind:
            path = path.with_suffix("."+kind)
            if path.exists() and QMessageBox.question(self,"Replace Export",f"Replace {path.name}?",QMessageBox.Yes|QMessageBox.Cancel)!=QMessageBox.Yes:
                return False
        try:
            export_vertices(path,self.model.vertices,kind)
        except (OSError,ValueError) as error:
            QMessageBox.warning(self,"Cannot Export",str(error))
            return False
        return True

    def show_controls(self):
        QMessageBox.information(self,"Part Editor — 3D Features",
            "Select Front, Right or Top Plane in the hierarchy, then New Sketch.\n"
            "Draw lines or three-point arcs, then close the outline to make a face. Dimensions use millimeters; arcs dimension by radius (R).\n"
            "Constraints: select straight lines for Horizontal/Vertical; Ctrl-click multiple lines for Equal. Delete relations or dimensions from the Constraints list to release them.\n"
            "Finish Sketch returns to the 3D view. Extrude adds material along the sketch normal.\n\n"
            "Click a flat model face (or choose it under Solid faces), then New Sketch to draw on it.\n"
            "While drawing, hover near a visible solid corner or edge to snap precisely to it. The locked marker shows the target; move away to release it. Sketch lines also snap.\n"
            "Double-click a sketch in the tree to edit it. Undo/redo includes sketches and extrusions.\n\n"
            "Backspace/Delete removes a selected sketch segment. Features → Delete Sketch / Delete Extrusion removes the selected tree item; deleting an extrusion keeps its sketch. Dependent sketches are listed before removal.\n\n"
            "3D: drag to orbit, middle-drag to pan, wheel to zoom, F to frame.\n"
            "Sketch: middle-drag to pan, wheel to zoom, double-click a segment to dimension.\n"
            "Choose Select line and drag an endpoint to move it within its constraints. Other endpoints stay fixed; Esc cancels and Ctrl+Z undoes the move.\n"
            "Cuts, fillets and curved-face sketches are not yet supported.")
