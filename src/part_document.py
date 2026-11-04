"""Editable sketch-part documents. Geometry uses meters; the UI shows mm."""
import copy
import json
from pathlib import Path
import uuid

from part_format import load_part
from sketch_geometry import Sketch
from temporary_parts import atomic_write


def new_document():
    return {"format":".simuOPart","version":2,"id":str(uuid.uuid4()),"name":"New part",
            "units":{"length":"m","mass":"kg","time":"s"},
            "coordinates":{"handedness":"right","up":"+Y"},
            "geometry":Sketch().geometry(),"appearance":{"color":"#47b9d5"},
            "material":{"name":"Default material","density":1000,"friction":.5,"restitution":.2},
            "physics":{"body_type":"dynamic","mass_source":"density","collider":"geometry"},
            "initial_state":{"position":[0,1,0],"velocity":[0,0,0]},"properties":{}}


def open_document(path):
    part = load_part(path,allow_draft=True)
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if part.sketch is not None:
        sketch = copy.deepcopy(part.sketch)
    else:
        x,y,z = part.size
        sketch = Sketch([[-x/2,-y/2],[x/2,-y/2],[x/2,y/2],[-x/2,y/2]],True,[None]*4,z)
    data["version"] = 2
    data["geometry"] = sketch.geometry()
    return data,sketch


def save_document(path,data,sketch):
    sketch.validate()
    saved = copy.deepcopy(data)
    saved["format"],saved["version"],saved["geometry"] = ".simuOPart",2,sketch.geometry()
    if not isinstance(saved.get("name"),str) or not saved["name"].strip():
        raise ValueError("Give the part a name before saving")
    atomic_write(path,json.dumps(saved,indent=2,allow_nan=False).encode("utf-8"))
    return saved
