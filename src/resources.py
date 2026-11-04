"""Locate shipped resources independently of the working directory."""

from pathlib import Path
import sys


def resource_path(*parts):
    base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
    return base.joinpath(*parts)
