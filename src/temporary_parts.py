"""Manage unsaved OBJ imports without modifying their source files."""

from pathlib import Path
import os
import tempfile


def atomic_write(path, contents):
    """Replace a file only after its complete contents have been written."""
    path = Path(path)
    staging = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            staging = Path(stream.name)
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staging, path)
    finally:
        # Windows cannot delete an open staging file. Leave the context before
        # cleanup on both write failures and replacement failures.
        if staging is not None:
            staging.unlink(missing_ok=True)


class TemporaryParts:
    def __init__(self):
        self._directory = None
        self.sources = {}

    @property
    def directory(self):
        return Path(self._directory.name) if self._directory else None

    def create(self, source):
        source = Path(source).resolve()
        # Snapshot the OBJ so moving/deleting the original cannot break the
        # imported part. The caller validates it before adding it to the scene.
        contents = source.read_bytes()
        if self._directory is None:
            self._directory = tempfile.TemporaryDirectory(prefix="simuo-parts-")
        name, number = source.stem, 1
        destination = self.directory / f"{name}.simuOPart"
        while destination.exists():
            number += 1
            destination = self.directory / f"{name}-{number}.simuOPart"
        destination.write_bytes(contents)
        self.sources[destination] = source
        return destination

    def contains(self, path):
        return path is not None and Path(path).resolve() in self.sources

    def release(self, path):
        path = Path(path).resolve()
        if path in self.sources:
            path.unlink(missing_ok=True)
            del self.sources[path]

    def cleanup(self):
        if self._directory:
            self._directory.cleanup()
        self._directory = None
        self.sources.clear()
