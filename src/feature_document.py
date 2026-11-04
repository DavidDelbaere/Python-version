"""Feature-part persistence and migration from the earlier sketch format."""
import copy
import json
from pathlib import Path

from feature_geometry import FeatureModel
from part_format import load_part
from part_document import new_document
from sketch_geometry import Sketch
from temporary_parts import atomic_write


def new_feature_document():
    data = new_document()
    data["version"],data["geometry"] = 3,FeatureModel().geometry()
    return data,FeatureModel()


def open_feature_document(path):
    part = load_part(path,allow_draft=True)
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if part.features is not None:
        return data,part.features
    model = FeatureModel()
    feature = model.new_sketch({"type":"plane","name":"Front"})
    if part.sketch is not None:
        sketch = copy.deepcopy(part.sketch)
        cx,cy = sketch.centroid
        sketch.points = [[x-cx,y-cy] for x,y in sketch.points]
    else:
        x,y,z = part.size
        sketch = Sketch([[-x/2,-y/2],[x/2,-y/2],[x/2,y/2],[-x/2,y/2]],True,[None]*4,z)
    feature["sketch"] = sketch.geometry()
    feature["depth"] = sketch.thickness if sketch.closed else None
    feature["symmetric"] = True
    model.build()
    data["version"],data["geometry"] = 3,model.geometry()
    return data,model


def save_feature_document(path,data,model):
    model.build()
    saved = copy.deepcopy(data)
    saved["format"],saved["version"],saved["geometry"] = ".simuOPart",3,model.geometry()
    if not isinstance(saved.get("name"),str) or not saved["name"].strip():
        raise ValueError("Give the part a name before saving")
    atomic_write(path,json.dumps(saved,indent=2,allow_nan=False).encode("utf-8"))
    return saved
