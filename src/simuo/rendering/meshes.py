"""Load OBJ-compatible mesh assets as flat-shaded vertex arrays."""

import numpy as np


def load_obj_flat_shaded(filename):
    """Load a Wavefront OBJ file and convert it to flat-shaded OpenGL vertex data.

    Args:
        filename: Path to the OBJ mesh file.

    Returns:
        numpy.ndarray: Interleaved position and normal data for each triangle.
    """
    positions = []
    output = []

    with open(
        filename,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        for line in file:
            data = line.split()

            if not data:
                continue

            if data[0] == "v":
                positions.append(
                    np.array(
                        [
                            float(data[1]),
                            float(data[2]),
                            float(data[3]),
                        ],
                        dtype=np.float32,
                    )
                )

            elif data[0] == "f":
                indices = []

                for token in data[1:]:
                    vertex_index = int(
                        token.split("/")[0]
                    )

                    if vertex_index < 0:
                        vertex_index = (
                            len(positions)
                            + vertex_index
                        )
                    else:
                        vertex_index -= 1

                    indices.append(
                        vertex_index
                    )

                # Convert polygon faces to triangles.
                for i in range(
                    1,
                    len(indices) - 1
                ):
                    p0 = positions[
                        indices[0]
                    ]

                    p1 = positions[
                        indices[i]
                    ]

                    p2 = positions[
                        indices[i + 1]
                    ]

                    edge1 = p1 - p0
                    edge2 = p2 - p0

                    normal = np.cross(
                        edge1,
                        edge2
                    )

                    length = np.linalg.norm(
                        normal
                    )

                    if length > 0.0:
                        normal = (
                            normal / length
                        )
                    else:
                        normal = np.array(
                            [0.0, 1.0, 0.0],
                            dtype=np.float32,
                        )

                    for point in (
                        p0,
                        p1,
                        p2
                    ):
                        output.extend(
                            [
                                point[0],
                                point[1],
                                point[2],
                                normal[0],
                                normal[1],
                                normal[2],
                            ]
                        )

    return np.asarray(
        output,
        dtype=np.float32,
    )
