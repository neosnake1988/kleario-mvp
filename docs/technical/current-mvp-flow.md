# Current MVP Flow

## Overview

The current MVP lets a user upload a text-based PDF, process it locally, and save a
searchable record. The stored file is not renamed or moved yet; the system stores a
proposed file name and folder as metadata.

## Backend Role

The FastAPI backend receives the upload, validates that it is a PDF, stores the
original file, extracts text, applies simple rules, and writes the result to SQLite.

The main backend flow starts in `app/backend/api/documents.py`.

## Frontend Role

The Next.js frontend provides one local interface for:

- choosing a PDF;
- uploading it to the backend;
- showing the latest result;
- listing saved documents;
- searching stored records;
- filtering by document type;
- correcting metadata;
- marking a document as validated;
- opening the original PDF.

The current UI is mainly in `app/frontend/app/page.tsx`.

## Upload PDF Flow

1. The user selects a PDF in the frontend.
2. The frontend sends it to `POST /documents/upload`.
3. The backend rejects non-PDF files.
4. The backend saves the original file locally.
5. The backend rejects files larger than 10 MB.
6. The backend processes the saved file and returns a public document record.

Controlled failures return structured API errors with a stable error code and a
human-readable message.

## Text Extraction Flow

Text extraction uses PyMuPDF. The MVP supports PDFs that already contain readable
text. Scanned PDFs are rejected until OCR is added.

The extraction logic is in `app/backend/services/text_extraction.py`.

## Document Classification Flow

The document type is detected with small keyword lists. The first supported rules
detect invoices, tax documents, and insurance documents. Unknown documents are
marked as `unknown`.

The classification rules are in `app/backend/services/document_detection.py`.

## Field Extraction Flow

The MVP extracts a few fields with simple rules:

- issuer;
- document date;
- amount;
- reference number.

The extraction rules are in `app/backend/services/field_extraction.py`.

## Proposed Name and Folder Flow

The backend builds a proposed file name and proposed folder from the detected type
and extracted fields. These values are stored as metadata only.

The naming rules are in `app/backend/services/naming.py`.

## Manual Correction and Validation Flow

The user can edit public metadata fields from the frontend. The frontend sends the
changes to `PATCH /documents/{id}/metadata`, and the backend stores the corrected
metadata in SQLite.

The user can also mark a reviewed document as `validated`. This updates metadata
only; it does not rename, move, or alter the original PDF.

## Original PDF Access Flow

The frontend opens the original PDF with `GET /documents/{id}/file`. The backend
looks up the stored file path internally and returns the PDF inline when possible.
The local storage path is never exposed to the frontend.

## Local File Storage

Uploaded originals are stored under `app/backend/storage/originals` by default.
The storage location can be changed with `KLEARIO_STORAGE_DIR`, which is useful for
tests and future storage changes.

The storage logic is in `app/backend/services/file_storage.py`.

## SQLite Storage

Processed document records are stored in SQLite under
`app/backend/data/kleario.sqlite3` by default.

The database path can be changed with `KLEARIO_DB_PATH`. Database setup, inserts,
listing, reading, and search are handled in `app/backend/database/db.py`.

## Search Flow

The frontend calls either `GET /documents` or `GET /documents/search?q=...`.
The backend searches metadata and extracted text with simple SQL `LIKE` queries.
The frontend can also apply a simple client-side document type filter.

## Current Limits

- Only PDF upload is supported.
- Only text-based PDFs are supported.
- OCR is not implemented yet.
- Direct image or photo upload is not supported.
- Classification uses keyword rules.
- Field extraction uses approximate regex rules.
- Proposed names and folders are not applied to the physical files.
- There is no authentication, access control, cloud storage, or background worker.
- The local MVP is not highly available and is not production cloud storage.

## How To Change Business Rules

- Change document type rules in `document_detection.py`.
- Change extracted fields in `field_extraction.py`.
- Change proposed names and folders in `naming.py`.

Keep business rules explicit and covered by focused tests when behavior changes.
