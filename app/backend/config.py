import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("KLEARIO_DATA_DIR", BASE_DIR / "data"))
DB_PATH = Path(os.getenv("KLEARIO_DB_PATH", DATA_DIR / "kleario.sqlite3"))
DEFAULT_STORAGE_DIR = BASE_DIR / "storage" / "originals"
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
