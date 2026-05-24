import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("KLEARIO_DATA_DIR", BASE_DIR / "data"))
DB_PATH = Path(os.getenv("KLEARIO_DB_PATH", DATA_DIR / "kleario.sqlite3"))


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_file_name TEXT NOT NULL,
                stored_file_path TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                extracted_text TEXT NOT NULL,
                document_type TEXT NOT NULL,
                issuer TEXT,
                document_date TEXT,
                amount TEXT,
                reference_number TEXT,
                proposed_file_name TEXT NOT NULL,
                proposed_folder TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def create_document(data: dict[str, Any]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    payload = {**data, "created_at": now, "updated_at": now}
    fields = ", ".join(payload.keys())
    placeholders = ", ".join(["?"] * len(payload))

    with get_connection() as connection:
        cursor = connection.execute(
            f"INSERT INTO documents ({fields}) VALUES ({placeholders})",
            list(payload.values()),
        )
        document_id = cursor.lastrowid

    document = get_document(document_id)
    if document is None:
        raise RuntimeError("Document was not created")
    return document


def list_documents() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM documents ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def get_document(document_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def search_documents(query: str) -> list[dict]:
    like_query = f"%{query.strip()}%"
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT * FROM documents
            WHERE original_file_name LIKE ?
               OR document_type LIKE ?
               OR issuer LIKE ?
               OR document_date LIKE ?
               OR amount LIKE ?
               OR reference_number LIKE ?
               OR proposed_file_name LIKE ?
               OR proposed_folder LIKE ?
               OR extracted_text LIKE ?
            ORDER BY created_at DESC
            """,
            [like_query] * 9,
        ).fetchall()
    return [dict(row) for row in rows]
