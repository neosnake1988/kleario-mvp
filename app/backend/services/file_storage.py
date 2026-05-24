import shutil
import uuid
from dataclasses import dataclass
import os
from pathlib import Path

from fastapi import UploadFile


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STORAGE_DIR = BASE_DIR / "storage" / "originals"


@dataclass(frozen=True)
class StoredFile:
    original_file_name: str
    path: Path
    file_size: int


def safe_file_name(file_name: str) -> str:
    """Keep uploaded file names local-path safe and readable."""
    cleaned = Path(file_name).name.replace(" ", "_")
    return "".join(char for char in cleaned if char.isalnum() or char in "._-")


async def save_upload_file(file: UploadFile) -> StoredFile:
    """Store the original uploaded file locally and return its metadata."""
    storage_dir = get_storage_dir()
    storage_dir.mkdir(parents=True, exist_ok=True)
    original_file_name = safe_file_name(file.filename or "document.pdf")
    stored_name = f"{uuid.uuid4().hex}_{original_file_name}"
    stored_path = storage_dir / stored_name

    with stored_path.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    return StoredFile(
        original_file_name=original_file_name,
        path=stored_path,
        file_size=stored_path.stat().st_size,
    )


def get_storage_dir() -> Path:
    """Return the local storage directory, overridable for tests."""
    return Path(os.getenv("KLEARIO_STORAGE_DIR", DEFAULT_STORAGE_DIR))
