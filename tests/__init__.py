"""Repository test suite; bootstrap the src layout once for source-checkout runs."""

from pathlib import Path
import sys

SOURCE_ROOT = Path(__file__).resolve().parent.parent / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
