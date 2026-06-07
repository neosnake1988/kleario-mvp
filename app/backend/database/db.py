import sqlite3
from datetime import datetime, timezone
from typing import Any

from config import DATA_DIR, DB_PATH


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


def update_document_metadata(document_id: int, data: dict[str, Any]) -> dict | None:
    if not data:
        return get_document(document_id)

    now = datetime.now(timezone.utc).isoformat()
    payload = {**data, "updated_at": now}
    assignments = ", ".join(f"{field} = ?" for field in payload)

    with get_connection() as connection:
        cursor = connection.execute(
            f"UPDATE documents SET {assignments} WHERE id = ?",
            [*payload.values(), document_id],
        )
        if cursor.rowcount == 0:
            return None

    return get_document(document_id)


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
