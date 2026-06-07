import os
import sys
from pathlib import Path
from unittest.mock import patch

import fitz
import pytest
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1] / "app" / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("KLEARIO_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("KLEARIO_DB_PATH", str(tmp_path / "data" / "test.sqlite3"))
    monkeypatch.setenv("KLEARIO_STORAGE_DIR", str(tmp_path / "storage" / "originals"))

    import database.db as db

    db.DATA_DIR = Path(os.environ["KLEARIO_DATA_DIR"])
    db.DB_PATH = Path(os.environ["KLEARIO_DB_PATH"])
    db.init_db()

    from main import app

    return TestClient(app)


def test_upload_pdf_extracts_and_saves_invoice(client, tmp_path):
    pdf_path = tmp_path / "invoice.pdf"
    create_pdf(
        pdf_path,
        "EDF\nFacture\nDate: 2026-05-12\nTotal TTC: 82,45\nReference: INV-123",
    )

    with pdf_path.open("rb") as pdf:
        response = client.post(
            "/documents/upload",
            files={"file": ("invoice.pdf", pdf, "application/pdf")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_type"] == "invoice"
    assert payload["issuer"] == "EDF"
    assert payload["document_date"] == "2026-05-12"
    assert payload["amount"] == "82.45"
    assert payload["reference_number"] == "INV-123"
    assert payload["proposed_file_name"] == "2026-05-12_EDF_invoice_82-45.pdf"
    assert payload["status"] == "processed"
    assert payload["original_filename"] == "invoice.pdf"


def test_rejects_non_pdf(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400


def test_rejects_pdf_without_readable_text(client, tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    create_empty_pdf(pdf_path)

    with pdf_path.open("rb") as pdf:
        response = client.post(
            "/documents/upload",
            files={"file": ("empty.pdf", pdf, "application/pdf")},
        )

    assert response.status_code == 400
    assert list((tmp_path / "storage" / "originals").iterdir()) == []


def test_rejects_pdf_over_10_mb_and_removes_stored_file(client, tmp_path):
    pdf_path = tmp_path / "large.pdf"
    pdf_path.write_bytes(b"%PDF-1.7\n" + b"0" * (10 * 1024 * 1024 + 1))

    with pdf_path.open("rb") as pdf:
        response = client.post(
            "/documents/upload",
            files={"file": ("large.pdf", pdf, "application/pdf")},
        )

    assert response.status_code == 413
    assert response.json()["detail"] == "PDF file is too large. Maximum size is 10 MB."
    assert list((tmp_path / "storage" / "originals").iterdir()) == []


def test_removes_stored_file_when_database_write_fails(client, tmp_path):
    pdf_path = tmp_path / "invoice.pdf"
    create_pdf(pdf_path, "EDF\nFacture\nTotal TTC: 82,45")

    with patch("api.documents.create_document", side_effect=RuntimeError("db failed")):
        with pdf_path.open("rb") as pdf:
            response = client.post(
                "/documents/upload",
                files={"file": ("invoice.pdf", pdf, "application/pdf")},
            )

    assert response.status_code == 500
    assert response.json()["detail"] == "The PDF could not be processed."
    assert list((tmp_path / "storage" / "originals").iterdir()) == []


def test_search_documents(client, tmp_path):
    pdf_path = tmp_path / "invoice.pdf"
    create_pdf(pdf_path, "EDF\nFacture\nTotal TTC: 82,45")

    with pdf_path.open("rb") as pdf:
        client.post(
            "/documents/upload",
            files={"file": ("invoice.pdf", pdf, "application/pdf")},
        )

    response = client.get("/documents/search", params={"q": "EDF"})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_public_document_responses_hide_internal_fields(client, tmp_path):
    pdf_path = tmp_path / "invoice.pdf"
    create_pdf(pdf_path, "EDF\nFacture\nTotal TTC: 82,45")

    with pdf_path.open("rb") as pdf:
        upload_response = client.post(
            "/documents/upload",
            files={"file": ("invoice.pdf", pdf, "application/pdf")},
        )

    assert upload_response.status_code == 200
    document_id = upload_response.json()["id"]

    list_response = client.get("/documents")
    search_response = client.get("/documents/search", params={"q": "EDF"})
    detail_response = client.get(f"/documents/{document_id}")

    public_documents = [
        upload_response.json(),
        list_response.json()[0],
        search_response.json()[0],
        detail_response.json(),
    ]
    for document in public_documents:
        assert "stored_file_path" not in document
        assert "extracted_text" not in document


def create_pdf(path: Path, text: str) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def create_empty_pdf(path: Path) -> None:
    document = fitz.open()
    document.new_page()
    document.save(path)
    document.close()
