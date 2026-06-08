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


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    assert_api_error(response, "INVALID_FILE_TYPE", "Only PDF files are supported")


def test_rejects_pdf_without_readable_text(client, tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    create_empty_pdf(pdf_path)

    with pdf_path.open("rb") as pdf:
        response = client.post(
            "/documents/upload",
            files={"file": ("empty.pdf", pdf, "application/pdf")},
        )

    assert response.status_code == 400
    assert_api_error(
        response,
        "PDF_TEXT_EXTRACTION_FAILED",
        "The PDF is invalid or could not be read.",
    )
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
    assert_api_error(
        response,
        "PDF_TOO_LARGE",
        "PDF file is too large. Maximum size is 10 MB.",
    )
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
    assert_api_error(response, "INTERNAL_ERROR", "The PDF could not be processed.")
    assert list((tmp_path / "storage" / "originals").iterdir()) == []


def test_get_document_returns_structured_not_found_error(client):
    response = client.get("/documents/999")

    assert response.status_code == 404
    assert_api_error(response, "DOCUMENT_NOT_FOUND", "Document not found")


def test_updates_document_metadata(client, tmp_path):
    document = upload_invoice(client, tmp_path)

    response = client.patch(
        f"/documents/{document['id']}/metadata",
        json={
            "document_type": "tax_document",
            "issuer": "Tax Office",
            "document_date": "2026-06-01",
            "amount": "120.00",
            "reference_number": "TAX-456",
            "proposed_file_name": "2026-06-01_Tax_Office_tax_document_120-00.pdf",
            "proposed_folder": "Administration/Taxes",
            "status": "reviewed",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["document_type"] == "tax_document"
    assert payload["issuer"] == "Tax Office"
    assert payload["document_date"] == "2026-06-01"
    assert payload["amount"] == "120.00"
    assert payload["reference_number"] == "TAX-456"
    assert (
        payload["proposed_file_name"]
        == "2026-06-01_Tax_Office_tax_document_120-00.pdf"
    )
    assert payload["proposed_folder"] == "Administration/Taxes"
    assert payload["status"] == "reviewed"
    assert "stored_file_path" not in payload
    assert "extracted_text" not in payload


def test_update_document_metadata_returns_not_found(client):
    response = client.patch(
        "/documents/999/metadata",
        json={"issuer": "Tax Office"},
    )

    assert response.status_code == 404
    assert_api_error(response, "DOCUMENT_NOT_FOUND", "Document not found")


def test_update_document_metadata_rejects_internal_fields(client, tmp_path):
    document = upload_invoice(client, tmp_path)

    for field in ("stored_file_path", "extracted_text"):
        response = client.patch(
            f"/documents/{document['id']}/metadata",
            json={field: "internal value"},
        )

        assert response.status_code == 400
        assert_api_error(
            response,
            "INVALID_METADATA_FIELD",
            f"Unsupported metadata field: {field}",
        )


def test_get_document_file_returns_pdf(client, tmp_path):
    document = upload_invoice(client, tmp_path)

    response = client.get(f"/documents/{document['id']}/file")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_get_document_file_returns_not_found_for_missing_document(client):
    response = client.get("/documents/999/file")

    assert response.status_code == 404
    assert_api_error(response, "DOCUMENT_NOT_FOUND", "Document not found")


def test_get_document_file_returns_error_when_physical_file_is_missing(
    client,
    tmp_path,
):
    document = upload_invoice(client, tmp_path)
    storage_dir = tmp_path / "storage" / "originals"
    for stored_file in storage_dir.iterdir():
        stored_file.unlink()

    response = client.get(f"/documents/{document['id']}/file")

    assert response.status_code == 404
    assert_api_error(
        response,
        "DOCUMENT_FILE_NOT_FOUND",
        "Original document file was not found.",
    )


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


def upload_invoice(client, tmp_path) -> dict:
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
    return response.json()


def assert_api_error(response, code: str, message: str) -> None:
    assert response.json()["detail"] == {
        "error": {
            "code": code,
            "message": message,
        }
    }
