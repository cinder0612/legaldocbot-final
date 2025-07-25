# patch_sqlite.py
import sys
try:
    import pysqlite3 as sqlite3
    sys.modules["sqlite3"] = sqlite3
except ImportError:
    pass   # fallback silencieux
