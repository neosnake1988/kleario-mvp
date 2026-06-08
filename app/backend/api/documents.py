from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.errors import api_error
from config import MAX_UPLOAD_SIZE_BYTES
from database.db import (
    create_document,
    get_document,
    list_documents,
    search_documents,
    update_document_metadata,
)
from services.document_detection import detect_document_type
from services.field_extraction import extract_fields
from services.file_storage import delete_stored_file, save_upload_file
from services.naming import build_proposed_file_name, build_proposed_folder
from services.text_extraction import PdfTextExtractionError, extract_text_from_pdf


router = APIRouter(prefix="/documents", tags=["documents"])
ALLOWED_METADATA_FIELDS = {
    "document_type",
    "issuer",
    "document_date",
    "amount",
    "reference_number",
    "proposed_file_name",
    "proposed_folder",
    "status",
}


def to_public_document(document: dict) -> dict:
    """Return the document fields exposed by the public API."""
    return {
        "id": document["id"],
        "original_filename": document["original_file_name"],
        "document_type": document["document_type"],
        "issuer": document.get("issuer"),
        "document_date": document.get("document_date"),
        "amount": document.get("amount"),
        "reference_number": document.get("reference_number"),
        "proposed_file_name": document["proposed_file_name"],
        "proposed_folder": document["proposed_folder"],
        "status": document["status"],
        "created_at": document["created_at"],
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    file_name = file.filename or ""
    has_pdf_extension = file_name.lower().endswith(".pdf")
    has_pdf_content_type = file.content_type in (None, "", "application/pdf")
    if not has_pdf_extension or not has_pdf_content_type:
        raise api_error(400, "INVALID_FILE_TYPE", "Only PDF files are supported")

    stored_file = await save_upload_file(file)
    try:
        if stored_file.file_size > MAX_UPLOAD_SIZE_BYTES:
            raise api_error(
                413,
                "PDF_TOO_LARGE",
                "PDF file is too large. Maximum size is 10 MB.",
            )

        extracted_text = extract_text_from_pdf(stored_file.path)

        document_type = detect_document_type(extracted_text)
        fields = extract_fields(extracted_text)
        proposed_file_name = build_proposed_file_name(
            document_type=document_type,
            original_file_name=stored_file.original_file_name,
            issuer=fields.get("issuer"),
            document_date=fields.get("document_date"),
            amount=fields.get("amount"),
        )
        proposed_folder = build_proposed_folder(
            document_type=document_type,
            issuer=fields.get("issuer"),
        )

        document = create_document(
            {
                "original_file_name": stored_file.original_file_name,
                "stored_file_path": str(stored_file.path),
                "mime_type": file.content_type or "application/pdf",
                "file_size": stored_file.file_size,
                "extracted_text": extracted_text,
                "document_type": document_type,
                "issuer": fields.get("issuer"),
                "document_date": fields.get("document_date"),
                "amount": fields.get("amount"),
                "reference_number": fields.get("reference_number"),
                "proposed_file_name": proposed_file_name,
                "proposed_folder": proposed_folder,
                "status": "processed",
            }
        )
    except PdfTextExtractionError as exc:
        delete_stored_file(stored_file)
        raise api_error(
            400,
            "PDF_TEXT_EXTRACTION_FAILED",
            "The PDF is invalid or could not be read.",
        ) from exc
    except HTTPException:
        delete_stored_file(stored_file)
        raise
    except Exception as exc:
        delete_stored_file(stored_file)
        raise api_error(500, "INTERNAL_ERROR", "The PDF could not be processed.") from exc

    return to_public_document(document)


@router.get("")
def get_documents() -> list[dict]:
    return [to_public_document(document) for document in list_documents()]


@router.get("/search")
def search(q: str) -> list[dict]:
    return [to_public_document(document) for document in search_documents(q)]


@router.patch("/{document_id}/metadata")
def patch_document_metadata(
    document_id: int,
    data: dict[str, Any] = Body(...),
) -> dict:
    invalid_fields = sorted(set(data) - ALLOWED_METADATA_FIELDS)
    if invalid_fields:
        raise api_error(
            400,
            "INVALID_METADATA_FIELD",
            f"Unsupported metadata field: {invalid_fields[0]}",
        )

    document = update_document_metadata(document_id, data)
    if document is None:
        raise api_error(404, "DOCUMENT_NOT_FOUND", "Document not found")
    return to_public_document(document)


@router.get("/{document_id}/file")
def get_document_file(document_id: int) -> FileResponse:
    document = get_document(document_id)
    if document is None:
        raise api_error(404, "DOCUMENT_NOT_FOUND", "Document not found")

    stored_file_path = Path(document["stored_file_path"])
    if not stored_file_path.is_file():
        raise api_error(
            404,
            "DOCUMENT_FILE_NOT_FOUND",
            "Original document file was not found.",
        )

    return FileResponse(
        stored_file_path,
        media_type="application/pdf",
        filename=document["original_file_name"],
    )


@router.get("/{document_id}")
def get_document_by_id(document_id: int) -> dict:
    document = get_document(document_id)
    if document is None:
        raise api_error(404, "DOCUMENT_NOT_FOUND", "Document not found")
    return to_public_document(document)
