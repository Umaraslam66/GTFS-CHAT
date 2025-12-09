import os
import sys
from pathlib import Path

# Provide minimal env defaults for settings during tests
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("TRAFIKLAB_API_KEY", "test-key")

# Ensure the backend package is importable in tests
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

