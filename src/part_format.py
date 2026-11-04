"""Validated SI JSON parts: v1 boxes, v2 sketches and v3 feature solids."""
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re


def number(value, label, minimum=None, maximum=None):
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{label} must be a finite number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must be <= {maximum}")
    return float(value)


def vector(value, label, positive=False):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label} must contain three numbers")
    result = tuple(number(x, label) for x in value)
    if positive and any(x <= 0 for x in result):
        raise ValueError(f"{label} components must be positive")
    return result


def fields(value, label, required, optional=()):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    if missing or unknown:
        raise ValueError(f"{label}: missing {sorted(missing)}, unsupported {sorted(unknown)}")
    return value


def string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


@dataclass(frozen=True)
class Part:
    id: str
    name: str
    size: tuple
    color: str
    density: float
    friction: float
    restitution: float
    body_type: str
    mass: float
    position: tuple
    velocity: tuple
    properties: dict
    mass_source: str = "density"
    sketch: object = None
    features: object = None

    @property
    def volume(self):
        if self.features is not None:
            return self.features.volume
        if self.sketch is not None:
            return abs(self.sketch.signed_area)*self.sketch.thickness
        return math.prod(self.size)

    @property
    def inertia(self):
        """Diagonal inertia about the geometric center, in kg m²."""
        x, y, z = self.size
        return tuple(self.mass * v / 12 for v in (y*y + z*z, x*x + z*z, x*x + y*y))

    def vertices(self, position):
        if self.features is not None:
            points = self.features.vertices.reshape(-1,6)[:,:3]
            return [tuple(p[i]+position[i] for i in range(3)) for p in points]
        if self.sketch is not None:
            cx,cy = self.sketch.centroid
            return [(position[0]+x-cx,position[1]+y-cy,position[2]+z)
                    for z in (-self.sketch.thickness/2,self.sketch.thickness/2)
                    for x,y in self.sketch.outline_points]
        x, y, z = (s / 2 for s in self.size)
        return [(position[0] + a, position[1] + b, position[2] + c)
                for a, b, c in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
                                (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]


def load_part(path, allow_draft=False):
    """Fail closed on unsupported physical semantics; properties are inert metadata."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"Non-finite JSON constant: {value}")

    with Path(path).open(encoding="utf-8-sig") as stream:
        d = json.load(stream, object_pairs_hook=unique_pairs, parse_constant=invalid_constant,
                      parse_float=lambda value: number(float(value), "JSON number"))
    fields(d, "part", ["format", "version", "id", "name", "units", "coordinates",
                       "geometry", "appearance", "material", "physics", "initial_state"],
           ["description", "properties"])
    if d["format"] != ".simuOPart" or type(d["version"]) is not int or d["version"] not in (1,2,3):
        raise ValueError("Expected .simuOPart version 1 (box), 2 (sketch), or 3 (features)")
    if d["units"] != {"length": "m", "mass": "kg", "time": "s"}:
        raise ValueError("Only SI units (m, kg, s) are supported")
    if d["coordinates"] != {"handedness": "right", "up": "+Y"}:
        raise ValueError("Expected right-handed coordinates with +Y up")
    sketch = None
    features = None
    if d["version"] == 1:
        g = fields(d["geometry"], "geometry", ["type", "size"])
        if g["type"] != "box":
            raise ValueError("SimuO part v1 supports solid boxes only")
        size = vector(g["size"], "geometry.size", positive=True)
        volume = math.prod(size)
    elif d["version"] == 2:
        from sketch_geometry import Sketch
        sketch = Sketch.from_geometry(d["geometry"])
        if not sketch.closed and not allow_draft:
            raise ValueError("This part is an unfinished sketch. Close its outline in the Part Editor before importing it.")
        xs = [p[0] for p in sketch.outline_points] or [0]
        ys = [p[1] for p in sketch.outline_points] or [0]
        size = (max(xs)-min(xs),max(ys)-min(ys),sketch.thickness)
        volume = abs(sketch.signed_area)*sketch.thickness
    else:
        from feature_geometry import FeatureModel
        features = FeatureModel.from_geometry(d["geometry"])
        if not features.has_solid and not allow_draft:
            raise ValueError("This part has no solid. Extrude a closed sketch in the Part Editor before importing it.")
        size,volume = features.size,features.volume
    draft = (sketch is not None and not sketch.closed) or (features is not None and not features.has_solid)
    a = fields(d["appearance"], "appearance", ["color"])
    if not isinstance(a["color"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", a["color"]):
        raise ValueError("appearance.color must be #RRGGBB")
    m = fields(d["material"], "material", ["name", "density", "friction", "restitution"])
    string(m["name"], "material.name")
    density = number(m["density"], "material.density", minimum=0)
    if density == 0:
        raise ValueError("material.density must be positive")
    friction = number(m["friction"], "material.friction", minimum=0)
    restitution = number(m["restitution"], "material.restitution", minimum=0, maximum=1)
    p = fields(d["physics"], "physics", ["body_type", "mass_source", "collider"], ["mass"])
    if p["body_type"] not in ("dynamic", "static") or p["collider"] != "geometry":
        raise ValueError("Expected dynamic/static body and collider=geometry")
    if p["mass_source"] == "density":
        if "mass" in p:
            raise ValueError("density mass source cannot also specify mass")
        mass = density * volume
    elif p["mass_source"] == "explicit":
        mass = number(p.get("mass"), "physics.mass", minimum=0)
    else:
        raise ValueError("mass_source must be density or explicit")
    if (mass <= 0 and not draft) or not math.isfinite(mass):
        raise ValueError("Part mass must be positive and finite")
    try:
        inertia = [mass * (size[i]**2 + size[j]**2) / 12 for i, j in [(1,2),(0,2),(0,1)]]
    except OverflowError as error:
        raise ValueError("Box inertia exceeds the supported numerical range") from error
    if any(not math.isfinite(v) or (v <= 0 and not draft) for v in inertia):
        raise ValueError("Derived box inertia must be positive and finite")
    state = fields(d["initial_state"], "initial_state", ["position", "velocity"])
    position = vector(state["position"], "initial_state.position")
    velocity = vector(state["velocity"], "initial_state.velocity")
    if p["body_type"] == "static" and any(velocity):
        raise ValueError("Static parts must have zero initial velocity")
    properties = d.get("properties", {})
    if not isinstance(properties, dict) or any(":" not in k for k in properties):
        raise ValueError("properties must be an object with namespaced keys (e.g. demo:tag)")
    if "description" in d:
        string(d["description"], "description")
    return Part(string(d["id"], "id"), string(d["name"], "name"), size, a["color"],
                density, friction, restitution, p["body_type"], mass, position, velocity, properties,
                p["mass_source"], sketch, features)
